from contextlib import asynccontextmanager

from fastapi import FastAPI

from aerospace_sim.api.routes import health, simulations, telemetry
from aerospace_sim.database.connection import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Autonomous Aerospace Simulator API",
    description="Secure simulation execution and SQL telemetry service.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(health.router)
app.include_router(simulations.router)
app.include_router(telemetry.router)
