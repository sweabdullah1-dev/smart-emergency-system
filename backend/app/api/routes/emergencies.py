from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.citizen import Citizen
from app.models.emergency import Emergency, EmergencyStatus
from app.models.user import User, UserRole
from app.schemas.emergency import AssignRequest, EmergencyCreate, EmergencyOut, EmergencyUpdate
from app.services.dispatch_service import assign_emergency
from app.services.notification_service import create_notification, notify_role
from app.services.simulation_service import reset_progress
from app.websocket.manager import manager

router = APIRouter(prefix="/emergencies", tags=["emergencies"])


@router.get("", response_model=list[EmergencyOut])
def list_emergencies(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = None,
):
    q = db.query(Emergency).order_by(Emergency.created_at.desc())
    if status:
        q = q.filter(Emergency.status == status)
    if user.role == UserRole.CITIZEN:
        citizen = db.query(Citizen).filter(Citizen.user_id == user.id).first()
        if citizen:
            q = q.filter(Emergency.citizen_id == citizen.id)
    return q.limit(100).all()


@router.get("/{emergency_id}", response_model=EmergencyOut)
def get_emergency(emergency_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    em = db.query(Emergency).filter(Emergency.id == emergency_id).first()
    if not em:
        raise HTTPException(404, "Emergency not found")
    return em


@router.post("", response_model=EmergencyOut)
async def create_emergency(
    body: EmergencyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    citizen_id = None
    if user.role in (UserRole.CITIZEN, UserRole.ADMIN):
        c = db.query(Citizen).filter(Citizen.user_id == user.id).first()
        if c:
            citizen_id = c.id

    em = Emergency(
        citizen_id=citizen_id,
        reporter_name=body.reporter_name,
        reporter_phone=body.reporter_phone,
        emergency_type=body.emergency_type,
        severity=body.severity,
        lat=body.lat,
        lng=body.lng,
        notes=body.notes,
        status=EmergencyStatus.PENDING,
    )
    db.add(em)
    db.commit()
    db.refresh(em)

    em = assign_emergency(db, em)
    await manager.broadcast({"type": "new_emergency", "emergency": EmergencyOut.model_validate(em).model_dump(mode="json")}, "dispatcher")
    await notify_role(db, UserRole.DISPATCHER, "New Emergency", f"Emergency #{em.id} - {em.severity.value}", "new_emergency", em.id, True)

    if user.role == UserRole.CITIZEN:
        await create_notification(db, user.id, "Emergency Submitted", f"Your emergency #{em.id} has been registered.", "emergency_created", em.id)

    return em


@router.post("/{emergency_id}/assign", response_model=EmergencyOut)
async def manual_assign(
    emergency_id: int,
    body: AssignRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN)),
):
    em = db.query(Emergency).filter(Emergency.id == emergency_id).first()
    if not em:
        raise HTTPException(404, "Not found")
    em = assign_emergency(db, em, body.ambulance_id, body.hospital_id)
    await manager.broadcast({"type": "emergency_assigned", "emergency_id": em.id}, "all")
    return em


@router.patch("/{emergency_id}", response_model=EmergencyOut)
async def update_emergency(
    emergency_id: int,
    body: EmergencyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    em = db.query(Emergency).filter(Emergency.id == emergency_id).first()
    if not em:
        raise HTTPException(404, "Not found")

    if body.status:
        em.status = body.status
        reset_progress(em.id)
        from app.models.status_log import StatusLog

        db.add(StatusLog(emergency_id=em.id, status=body.status.value))
    if body.ambulance_id is not None:
        em.ambulance_id = body.ambulance_id
    if body.hospital_id is not None:
        em.hospital_id = body.hospital_id

    db.commit()
    db.refresh(em)
    await manager.broadcast({"type": "emergency_update", "emergency": EmergencyOut.model_validate(em).model_dump(mode="json")}, "all")
    return em


@router.post("/{emergency_id}/accept", response_model=EmergencyOut)
async def driver_accept(
    emergency_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.DRIVER)),
):
    from app.models.driver import Driver
    from app.models.ambulance import AmbulanceStatus

    em = db.query(Emergency).filter(Emergency.id == emergency_id).first()
    if not em:
        raise HTTPException(404, "Not found")
    driver = db.query(Driver).filter(Driver.user_id == user.id).first()
    if driver and em.ambulance_id:
        em.status = EmergencyStatus.ACCEPTED
        from app.models.ambulance import Ambulance

        amb = db.query(Ambulance).filter(Ambulance.id == em.ambulance_id).first()
        if amb:
            amb.status = AmbulanceStatus.EN_ROUTE
        em.status = EmergencyStatus.EN_ROUTE
        db.commit()
        db.refresh(em)
        reset_progress(em.id)
        await create_notification(db, user.id, "Emergency Accepted", f"Navigate to emergency #{em.id}", "driver_accepted", em.id, True)
        await manager.broadcast({"type": "driver_accepted", "emergency_id": em.id}, "all")
    return em


@router.post("/{emergency_id}/status/{new_status}", response_model=EmergencyOut)
async def update_status(
    emergency_id: int,
    new_status: EmergencyStatus,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.DRIVER, UserRole.DISPATCHER, UserRole.ADMIN)),
):
    from app.models.ambulance import Ambulance, AmbulanceStatus
    from app.models.status_log import StatusLog
    from app.services.route_optimizer import compute_route
    from app.services.traffic_service import get_traffic_penalty_fn

    em = db.query(Emergency).filter(Emergency.id == emergency_id).first()
    if not em:
        raise HTTPException(404, "Not found")

    em.status = new_status
    db.add(StatusLog(emergency_id=em.id, status=new_status.value))

    if new_status == EmergencyStatus.PICKED_UP and em.hospital_id:
        from app.models.hospital import Hospital

        h = db.query(Hospital).filter(Hospital.id == em.hospital_id).first()
        amb = db.query(Ambulance).filter(Ambulance.id == em.ambulance_id).first()
        if h and amb:
            penalty = get_traffic_penalty_fn(db)
            route = compute_route(amb.lat, amb.lng, h.lat, h.lng, "astar", penalty)
            em.route_polyline = route.polyline_json
            em.eta_minutes = route.eta_minutes
            em.status = EmergencyStatus.TRANSPORTING
            amb.status = AmbulanceStatus.TRANSPORTING
            reset_progress(em.id)

    if new_status == EmergencyStatus.COMPLETED:
        amb = db.query(Ambulance).filter(Ambulance.id == em.ambulance_id).first()
        if amb:
            amb.status = AmbulanceStatus.AVAILABLE

    db.commit()
    db.refresh(em)
    await manager.broadcast({"type": "status_update", "emergency_id": em.id, "status": em.status.value}, "all")
    return em
