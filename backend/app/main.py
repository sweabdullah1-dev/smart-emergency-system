"""Smart Emergency Priority System - FastAPI application."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.seed import seed_if_empty
from app.db.session import SessionLocal
from app.api.routes import (
    auth,
    emergencies,
    ambulances,
    hospitals,
    routes,
    analytics,
    notifications,
    traffic,
    citizens,
    drivers,
    dispatchers,
)
from app.services.simulation_service import tick_simulation
from app.websocket.manager import manager

_simulation_task: asyncio.Task | None = None


async def simulation_loop():
    while True:
        try:
            db = SessionLocal()
            events = tick_simulation(db)
            for ev in events:
                await manager.broadcast(ev, "all")
            db.close()
        except Exception as e:
            print(f"Simulation tick error: {e}")
        await asyncio.sleep(settings.SIMULATION_TICK_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _simulation_task
    seed_if_empty()
    _simulation_task = asyncio.create_task(simulation_loop())
    yield
    if _simulation_task:
        _simulation_task.cancel()


app = FastAPI(
    title="Smart Emergency Priority System",
    description="Simulation platform for national emergency dispatch (not connected to real services).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(emergencies.router, prefix=API_PREFIX)
app.include_router(ambulances.router, prefix=API_PREFIX)
app.include_router(hospitals.router, prefix=API_PREFIX)
app.include_router(routes.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
app.include_router(notifications.router, prefix=API_PREFIX)
app.include_router(traffic.router, prefix=API_PREFIX)
app.include_router(citizens.router, prefix=API_PREFIX)
app.include_router(drivers.router, prefix=API_PREFIX)
app.include_router(dispatchers.router, prefix=API_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "service": "Smart Emergency Priority System"}


@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str = "all"):
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
