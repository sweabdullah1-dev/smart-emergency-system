from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.hospital import Hospital

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("")
def list_hospitals(city: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Hospital)
    if city:
        q = q.filter(Hospital.city.ilike(f"%{city}%"))
    return [
        {
            "id": h.id,
            "name": h.name,
            "name_ar": h.name_ar,
            "city": h.city,
            "lat": h.lat,
            "lng": h.lng,
            "capacity": h.capacity,
            "current_load": h.current_load,
            "emergency_available": h.emergency_available,
            "hospital_type": h.hospital_type.value,
            "load_percent": round(100 * h.current_load / max(h.capacity, 1), 1),
        }
        for h in q.all()
    ]


@router.get("/{hospital_id}")
def get_hospital(hospital_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    h = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not h:
        from fastapi import HTTPException
        raise HTTPException(404)
    return h
