from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.services.route_optimizer import compute_route
from app.services.traffic_service import get_traffic_penalty_fn

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("/compute")
def compute(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    algorithm: str = "astar",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    penalty = get_traffic_penalty_fn(db)
    result = compute_route(start_lat, start_lng, end_lat, end_lng, algorithm, penalty)
    return {
        "algorithm": result.algorithm,
        "distance_km": result.distance_km,
        "eta_minutes": result.eta_minutes,
        "polyline": result.polyline_json,
        "path": result.path,
    }
