"""Simulates live ambulance movement along computed routes."""
from __future__ import annotations

import json
import math
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.ambulance import Ambulance, AmbulanceStatus
from app.models.emergency import Emergency, EmergencyStatus
from app.models.gps_tracking import GPSTracking
from app.services.route_optimizer import haversine_km


def _interpolate_path(polyline: str, progress: float) -> tuple[float, float]:
    """Get position along polyline at progress 0..1."""
    try:
        points = json.loads(polyline)
    except (json.JSONDecodeError, TypeError):
        return (0.0, 0.0)
    if not points or len(points) < 2:
        return (points[0][0], points[0][1]) if points else (0.0, 0.0)

    total = 0.0
    segments = []
    for i in range(len(points) - 1):
        d = haversine_km(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
        segments.append(d)
        total += d

    if total == 0:
        return (points[-1][0], points[-1][1])

    target = total * min(max(progress, 0), 1)
    acc = 0.0
    for i, seg_len in enumerate(segments):
        if acc + seg_len >= target:
            t = (target - acc) / seg_len if seg_len else 0
            lat = points[i][0] + t * (points[i + 1][0] - points[i][0])
            lng = points[i][1] + t * (points[i + 1][1] - points[i][1])
            return (lat, lng)
        acc += seg_len
    return (points[-1][0], points[-1][1])


# In-memory progress per emergency (simulation)
_progress: dict[int, float] = {}


def tick_simulation(db: Session) -> list[dict]:
    """Advance ambulances toward targets; returns broadcast events."""
    events: list[dict] = []
    active = (
        db.query(Emergency)
        .filter(
            Emergency.status.in_(
                [
                    EmergencyStatus.ACCEPTED,
                    EmergencyStatus.EN_ROUTE,
                    EmergencyStatus.ON_SCENE,
                    EmergencyStatus.PICKED_UP,
                    EmergencyStatus.TRANSPORTING,
                ]
            )
        )
        .all()
    )

    for em in active:
        if not em.ambulance_id or not em.route_polyline:
            continue
        amb = db.query(Ambulance).filter(Ambulance.id == em.ambulance_id).first()
        if not amb:
            continue

        prog = _progress.get(em.id, 0.0) + 0.08
        target_lat, target_lng = em.lat, em.lng
        if em.status in (EmergencyStatus.PICKED_UP, EmergencyStatus.TRANSPORTING) and em.hospital_id:
            from app.models.hospital import Hospital

            h = db.query(Hospital).filter(Hospital.id == em.hospital_id).first()
            if h:
                target_lat, target_lng = h.lat, h.lng
                if em.status == EmergencyStatus.TRANSPORTING and em.route_polyline:
                    from app.services.route_optimizer import compute_route
                    from app.services.traffic_service import get_traffic_penalty_fn

                    penalty = get_traffic_penalty_fn(db)
                    r = compute_route(amb.lat, amb.lng, h.lat, h.lng, "astar", penalty)
                    em.route_polyline = r.polyline_json
                    em.eta_minutes = r.eta_minutes * (1 - prog)

        lat, lng = _interpolate_path(em.route_polyline or "[]", prog)
        amb.lat = lat
        amb.lng = lng
        amb.last_updated = datetime.utcnow()

        db.add(GPSTracking(ambulance_id=amb.id, lat=lat, lng=lng, speed_kmh=45.0))

        dist_remain = haversine_km(lat, lng, target_lat, target_lng)
        if dist_remain < 0.3 and em.status == EmergencyStatus.EN_ROUTE:
            em.status = EmergencyStatus.ON_SCENE
            amb.status = AmbulanceStatus.ON_SCENE
            prog = 0
            from app.models.status_log import StatusLog

            db.add(StatusLog(emergency_id=em.id, status=EmergencyStatus.ON_SCENE.value))
        elif dist_remain < 0.3 and em.status == EmergencyStatus.TRANSPORTING:
            em.status = EmergencyStatus.ARRIVED_HOSPITAL
            amb.status = AmbulanceStatus.AVAILABLE
            em.completed_at = datetime.utcnow()
            prog = 1.0

        _progress[em.id] = min(prog, 1.0)
        if em.eta_minutes:
            em.eta_minutes = max(0, em.eta_minutes - 0.15)

        events.append(
            {
                "type": "ambulance_position",
                "ambulance_id": amb.id,
                "emergency_id": em.id,
                "lat": lat,
                "lng": lng,
                "eta_minutes": em.eta_minutes,
                "status": em.status.value,
            }
        )

    db.commit()
    return events


def reset_progress(emergency_id: int) -> None:
    _progress[emergency_id] = 0.0
