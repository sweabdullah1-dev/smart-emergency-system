"""
Smart ambulance and hospital assignment engine.
Priority: critical emergencies > closest available > fastest ETA > avoid traffic.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.ambulance import Ambulance, AmbulanceStatus
from app.models.emergency import Emergency, EmergencyStatus, SeverityLevel
from app.models.hospital import Hospital
from app.models.route import Route
from app.models.status_log import StatusLog
from app.models.traffic import TrafficZone
from app.services.route_optimizer import compute_route, haversine_km
from app.services.traffic_service import get_traffic_penalty_fn


SEVERITY_WEIGHT = {
    SeverityLevel.CRITICAL: 1000,
    SeverityLevel.HIGH: 500,
    SeverityLevel.MEDIUM: 200,
    SeverityLevel.LOW: 50,
}


def _ambulance_score(
    db: Session,
    amb: Ambulance,
    emergency: Emergency,
    penalty_fn,
) -> tuple[float, float, float]:
    """Returns (priority_score, distance_km, eta_minutes). Lower ETA is better."""
    if amb.status not in (AmbulanceStatus.AVAILABLE,):
        return (-1, 9999, 9999)

    route = compute_route(amb.lat, amb.lng, emergency.lat, emergency.lng, "astar", penalty_fn)
    dist = route.distance_km
    eta = route.eta_minutes
    priority = SEVERITY_WEIGHT.get(emergency.severity, 100) - (eta * 2) - (dist * 0.5)
    return (priority, dist, eta)


def find_best_ambulance(db: Session, emergency: Emergency) -> Ambulance | None:
    penalty_fn = get_traffic_penalty_fn(db)
    ambulances = db.query(Ambulance).filter(Ambulance.status == AmbulanceStatus.AVAILABLE).all()
    if not ambulances:
        return None

    best: Ambulance | None = None
    best_eta = float("inf")
    best_score = float("-inf")

    for amb in ambulances:
        score, dist, eta = _ambulance_score(db, amb, emergency, penalty_fn)
        if score < 0:
            continue
        # Critical: prefer lowest ETA; tie-break by score
        if emergency.severity == SeverityLevel.CRITICAL:
            if eta < best_eta:
                best_eta = eta
                best_score = score
                best = amb
        elif score > best_score:
            best_score = score
            best_eta = eta
            best = amb

    return best


def find_best_hospital(db: Session, emergency: Emergency) -> Hospital | None:
    penalty_fn = get_traffic_penalty_fn(db)
    hospitals = (
        db.query(Hospital)
        .filter(Hospital.emergency_available == True)  # noqa: E712
        .all()
    )
    if not hospitals:
        return None

    best: Hospital | None = None
    best_score = float("inf")

    for h in hospitals:
        if h.current_load >= h.capacity:
            continue
        route = compute_route(emergency.lat, emergency.lng, h.lat, h.lng, "astar", penalty_fn)
        load_factor = h.current_load / max(h.capacity, 1)
        severity_bonus = 0
        if emergency.severity in (SeverityLevel.CRITICAL, SeverityLevel.HIGH):
            if h.hospital_type.value == "trauma":
                severity_bonus = -5
        score = route.eta_minutes + (load_factor * 10) + severity_bonus
        if score < best_score:
            best_score = score
            best = h

    return best


def assign_emergency(db: Session, emergency: Emergency, ambulance_id: int | None = None, hospital_id: int | None = None) -> Emergency:
    penalty_fn = get_traffic_penalty_fn(db)

    if not hospital_id:
        hospital = find_best_hospital(db, emergency)
        if hospital:
            emergency.hospital_id = hospital.id
    else:
        emergency.hospital_id = hospital_id

    if ambulance_id:
        amb = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    else:
        amb = find_best_ambulance(db, emergency)

    if amb:
        route = compute_route(amb.lat, amb.lng, emergency.lat, emergency.lng, "astar", penalty_fn)
        emergency.ambulance_id = amb.id
        emergency.status = EmergencyStatus.ASSIGNED
        emergency.eta_minutes = route.eta_minutes
        emergency.route_polyline = route.polyline_json
        emergency.priority_score = int(SEVERITY_WEIGHT.get(emergency.severity, 0))
        emergency.auto_assigned = ambulance_id is None

        amb.status = AmbulanceStatus.DISPATCHED

        db.add(
            Route(
                emergency_id=emergency.id,
                algorithm=route.algorithm,
                polyline=route.polyline_json,
                distance_km=route.distance_km,
                eta_minutes=route.eta_minutes,
            )
        )
        db.add(StatusLog(emergency_id=emergency.id, status=EmergencyStatus.ASSIGNED.value, note="Auto-assigned ambulance"))

    db.commit()
    db.refresh(emergency)
    return emergency
