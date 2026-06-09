from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from aerospace_sim.api.schemas import HealthResponse
from aerospace_sim.database.connection import get_db


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(
        status="ok",
        service="autonomous-aerospace-simulator",
        database="available",
    )
