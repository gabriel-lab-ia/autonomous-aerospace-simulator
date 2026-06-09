from collections.abc import AsyncGenerator, Generator

import httpx2
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from aerospace_sim.api.main import app
from aerospace_sim.database.connection import Base, get_db


TEST_API_KEY = "test-api-key"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client(tmp_path, monkeypatch) -> AsyncGenerator[httpx2.AsyncClient, None]:
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        session = test_session()
        try:
            yield session
        finally:
            session.close()

    monkeypatch.setenv("AEROSPACE_API_KEY", TEST_API_KEY)
    app.dependency_overrides[get_db] = override_get_db
    transport = httpx2.ASGITransport(app=app)
    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def auth_headers() -> dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}


@pytest.mark.anyio
async def test_health_is_public_and_database_is_available(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "autonomous-aerospace-simulator",
        "database": "available",
    }


@pytest.mark.anyio
async def test_protected_endpoint_requires_valid_api_key(
    client: httpx2.AsyncClient,
) -> None:
    assert (await client.get("/simulations")).status_code == 401
    invalid = await client.get("/simulations", headers={"X-API-Key": "invalid"})
    assert invalid.status_code == 403


@pytest.mark.anyio
async def test_protected_endpoint_rejects_unconfigured_authentication(
    client: httpx2.AsyncClient,
    monkeypatch,
) -> None:
    monkeypatch.delenv("AEROSPACE_API_KEY")

    response = await client.get("/simulations", headers=auth_headers())

    assert response.status_code == 503


@pytest.mark.anyio
async def test_basic_simulation_is_persisted_with_telemetry(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.post(
        "/simulations/basic",
        headers=auth_headers(),
        json={"steps": 5, "throttle": 0.5},
    )

    assert response.status_code == 201
    simulation = response.json()
    assert simulation["simulation_type"] == "basic"
    assert simulation["status"] == "completed"

    simulation_id = simulation["id"]
    telemetry_response = await client.get(
        f"/telemetry/{simulation_id}",
        headers=auth_headers(),
    )
    assert telemetry_response.status_code == 200
    assert len(telemetry_response.json()) == 6

    list_response = await client.get("/simulations?limit=10", headers=auth_headers())
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == simulation_id


@pytest.mark.anyio
async def test_landing_and_heuristic_endpoints_persist_results(
    client: httpx2.AsyncClient,
) -> None:
    landing = await client.post(
        "/simulations/landing",
        headers=auth_headers(),
        json={"max_steps": 10, "throttle": 0.0},
    )
    heuristic = await client.post(
        "/simulations/heuristic-landing",
        headers=auth_headers(),
        json={"max_steps": 10},
    )

    assert landing.status_code == 201
    assert landing.json()["simulation_type"] == "landing"
    assert heuristic.status_code == 201
    assert heuristic.json()["simulation_type"] == "heuristic_landing"


@pytest.mark.anyio
async def test_invalid_request_and_missing_resources_return_expected_statuses(
    client: httpx2.AsyncClient,
) -> None:
    invalid = await client.post(
        "/simulations/basic",
        headers=auth_headers(),
        json={"throttle": 2.0},
    )

    assert invalid.status_code == 422
    missing_simulation = await client.get("/simulations/999", headers=auth_headers())
    missing_telemetry = await client.get("/telemetry/999", headers=auth_headers())
    assert missing_simulation.status_code == 404
    assert missing_telemetry.status_code == 404
