from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from aerospace_sim.api import execution
from aerospace_sim.api.auth import require_api_key
from aerospace_sim.api.schemas import (
    BasicSimulationRequest,
    HeuristicLandingSimulationRequest,
    LandingSimulationRequest,
    SimulationResponse,
)
from aerospace_sim.database import crud
from aerospace_sim.database.connection import get_db
from aerospace_sim.database.models import SimulationModel


router = APIRouter(
    prefix="/simulations",
    tags=["simulations"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/basic", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def create_basic_simulation(
    request: BasicSimulationRequest,
    db: Session = Depends(get_db),
) -> SimulationResponse:
    result = execution.run_basic_simulation(**request.model_dump())
    return SimulationResponse.model_validate(_persist(db, result))


@router.post("/landing", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def create_landing_simulation(
    request: LandingSimulationRequest,
    db: Session = Depends(get_db),
) -> SimulationResponse:
    result = execution.run_fixed_throttle_landing(**request.model_dump())
    return SimulationResponse.model_validate(_persist(db, result))


@router.post(
    "/heuristic-landing",
    response_model=SimulationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_heuristic_landing_simulation(
    request: HeuristicLandingSimulationRequest,
    db: Session = Depends(get_db),
) -> SimulationResponse:
    result = execution.run_heuristic_landing(**request.model_dump())
    return SimulationResponse.model_validate(_persist(db, result))


@router.get("", response_model=list[SimulationResponse])
def get_simulations(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    simulation_type: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    db: Session = Depends(get_db),
) -> list[SimulationResponse]:
    simulations = crud.list_simulations(
        db,
        limit=limit,
        simulation_type=simulation_type,
        status=status_filter,
    )
    return [SimulationResponse.model_validate(item) for item in simulations]


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: int, db: Session = Depends(get_db)) -> SimulationResponse:
    simulation = crud.get_simulation(db, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found.")
    return SimulationResponse.model_validate(simulation)


def _persist(db: Session, result: execution.SimulationExecution) -> SimulationModel:
    initial = result.initial_state
    final = result.final_state
    return crud.create_simulation(
        db,
        simulation_type=result.simulation_type,
        status=result.status,
        reason=result.reason,
        initial_altitude_m=initial.altitude,
        initial_vertical_velocity_m_s=initial.velocity.z,
        initial_fuel_mass_kg=initial.fuel_mass,
        final_altitude_m=final.altitude,
        final_vertical_velocity_m_s=final.velocity.z,
        final_speed_m_s=final.speed,
        final_fuel_mass_kg=final.fuel_mass,
        final_time_s=final.time,
        metadata_json=result.metadata_json,
        telemetry=result.telemetry,
    )
