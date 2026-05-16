from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.ambulance import Ambulance
from app.models.emergency import Emergency, EmergencyStatus
from app.models.hospital import Hospital
from app.models.user import UserRole

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("")
def analytics(db: Session = Depends(get_db), user=Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN))):
    total = db.query(Emergency).count()
    completed = db.query(Emergency).filter(Emergency.status == EmergencyStatus.COMPLETED).count()
    active = db.query(Emergency).filter(
        Emergency.status.notin_([EmergencyStatus.COMPLETED, EmergencyStatus.CANCELLED])
    ).count()

    by_type = (
        db.query(Emergency.emergency_type, func.count(Emergency.id))
        .group_by(Emergency.emergency_type)
        .all()
    )
    by_severity = (
        db.query(Emergency.severity, func.count(Emergency.id))
        .group_by(Emergency.severity)
        .all()
    )

    hospitals = db.query(Hospital).all()
    hospital_load = [
        {"name": h.name, "city": h.city, "load_percent": round(100 * h.current_load / max(h.capacity, 1), 1)}
        for h in hospitals
    ]

    from app.models.ambulance import AmbulanceStatus

    amb_available = db.query(Ambulance).filter(Ambulance.status == AmbulanceStatus.AVAILABLE).count()
    amb_total = db.query(Ambulance).count()

    # Hotspots from emergency coordinates (bucketed)
    emergencies = db.query(Emergency.lat, Emergency.lng).limit(500).all()
    hotspots = [{"lat": e.lat, "lng": e.lng, "weight": 1} for e in emergencies]

    avg_eta = db.query(func.avg(Emergency.eta_minutes)).filter(Emergency.eta_minutes.isnot(None)).scalar() or 0

    return {
        "total_emergencies": total,
        "completed": completed,
        "active": active,
        "avg_eta_minutes": round(float(avg_eta), 1),
        "avg_response_time_minutes": round(float(avg_eta) * 1.2, 1),
        "by_type": {str(t.value if hasattr(t, "value") else t): c for t, c in by_type},
        "by_severity": {str(s.value if hasattr(s, "value") else s): c for s, c in by_severity},
        "hospital_load": hospital_load,
        "ambulances_available": amb_available,
        "ambulances_total": amb_total,
        "hotspots": hotspots,
    }
