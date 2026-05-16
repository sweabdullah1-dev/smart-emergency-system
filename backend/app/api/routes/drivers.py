from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.ambulance import Ambulance
from app.models.driver import Driver
from app.models.emergency import Emergency, EmergencyStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("/assignments")
def my_assignments(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.DRIVER))):
    driver = db.query(Driver).filter(Driver.user_id == user.id).first()
    if not driver:
        return []
    amb = db.query(Ambulance).filter(Ambulance.driver_id == driver.id).first()
    if not amb:
        return []
    ems = (
        db.query(Emergency)
        .filter(
            Emergency.ambulance_id == amb.id,
            Emergency.status.notin_([EmergencyStatus.COMPLETED, EmergencyStatus.CANCELLED]),
        )
        .all()
    )
    return [{"emergency": e, "ambulance_id": amb.id} for e in ems]
