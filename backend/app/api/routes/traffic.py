from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.traffic import TrafficZone

router = APIRouter(prefix="/traffic", tags=["traffic"])


@router.get("")
def list_traffic(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [
        {
            "id": z.id,
            "name": z.name,
            "city": z.city,
            "center_lat": z.center_lat,
            "center_lng": z.center_lng,
            "radius_km": z.radius_km,
            "level": z.level.value,
            "speed_factor": z.speed_factor,
        }
        for z in db.query(TrafficZone).all()
    ]
