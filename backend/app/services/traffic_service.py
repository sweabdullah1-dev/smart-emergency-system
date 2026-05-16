"""Traffic zone penalties for route optimization."""
from sqlalchemy.orm import Session

from app.models.traffic import TrafficLevel, TrafficZone
from app.services.route_optimizer import haversine_km


def get_traffic_penalty_fn(db: Session) -> callable:
    zones = db.query(TrafficZone).all()

    def penalty(lat: float, lng: float) -> float:
        max_penalty = 1.0
        for z in zones:
            dist = haversine_km(lat, lng, z.center_lat, z.center_lng)
            if dist <= z.radius_km:
                factor = z.speed_factor
                if z.level == TrafficLevel.RED:
                    factor = min(factor, 0.4)
                elif z.level == TrafficLevel.YELLOW:
                    factor = min(factor, 0.7)
                max_penalty = max(max_penalty, 1.0 / max(factor, 0.1))
        return max_penalty

    return penalty
