from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.ambulance import Ambulance

router = APIRouter(prefix="/ambulances", tags=["ambulances"])


@router.get("")
def list_ambulances(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [
        {
            "id": a.id,
            "plate_number": a.plate_number,
            "lat": a.lat,
            "lng": a.lng,
            "status": a.status.value,
            "city": a.city,
            "driver_id": a.driver_id,
        }
        for a in db.query(Ambulance).all()
    ]


@router.get("/nearby")
def nearby_ambulances(lat: float, lng: float, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from app.services.route_optimizer import haversine_km

    result = []
    for a in db.query(Ambulance).all():
        dist = haversine_km(lat, lng, a.lat, a.lng)
        result.append({"id": a.id, "plate_number": a.plate_number, "lat": a.lat, "lng": a.lng, "status": a.status.value, "distance_km": round(dist, 2)})
    result.sort(key=lambda x: x["distance_km"])
    return result[:10]
