from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.citizen import Citizen
from app.models.user import User, UserRole

router = APIRouter(prefix="/citizens", tags=["citizens"])


@router.get("/me")
def my_profile(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CITIZEN, UserRole.ADMIN))):
    c = db.query(Citizen).filter(Citizen.user_id == user.id).first()
    return {"user_id": user.id, "citizen_id": c.id if c else None, "default_lat": c.default_lat if c else None, "default_lng": c.default_lng if c else None}
