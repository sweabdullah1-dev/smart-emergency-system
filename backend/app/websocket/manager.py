"""WebSocket connection manager for real-time updates."""
from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {
            "all": [],
            "dispatcher": [],
            "driver": [],
            "citizen": [],
            "hospital": [],
        }

    async def connect(self, websocket: WebSocket, channel: str = "all", user_id: int | None = None):
        await websocket.accept()
        key = channel if channel in self.active else "all"
        self.active[key].append(websocket)
        if user_id:
            uid_key = f"user_{user_id}"
            self.active.setdefault(uid_key, []).append(websocket)

    def disconnect(self, websocket: WebSocket):
        for conns in self.active.values():
            if websocket in conns:
                conns.remove(websocket)

    async def broadcast(self, message: dict[str, Any], channel: str = "all"):
        data = json.dumps(message, default=str)
        targets = list(self.active.get(channel, [])) + list(self.active.get("all", []))
        dead = []
        for ws in set(targets):
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_user(self, user_id: int, message: dict[str, Any]):
        await self.broadcast(message, f"user_{user_id}")


manager = ConnectionManager()
