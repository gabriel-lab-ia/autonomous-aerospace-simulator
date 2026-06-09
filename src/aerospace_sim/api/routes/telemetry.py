from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from aerospace_sim.api.auth import require_api_key
from aerospace_sim.api.schemas import TelemetryPointResponse
from aerospace_sim.database import crud
from aerospace_sim.database.connection import get_db


router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/{simulation_id}", response_model=list[TelemetryPointResponse])
def get_telemetry(
    simulation_id: int,
    limit: Annotated[int, Query(ge=1, le=10_000)] = 1000,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[TelemetryPointResponse]:
    if crud.get_simulation(db, simulation_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")
    telemetry = crud.list_telemetry(
        db,
        simulation_id=simulation_id,
        limit=limit,
        offset=offset,
    )
    return [TelemetryPointResponse.model_validate(point) for point in telemetry]
