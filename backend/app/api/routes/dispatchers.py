from fastapi import APIRouter, Depends

from app.api.deps import require_roles
from app.models.user import UserRole

router = APIRouter(prefix="/dispatchers", tags=["dispatchers"])


@router.get("/dashboard")
def dashboard(user=Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN))):
    return {"status": "ok", "message": "Use /emergencies, /ambulances, /analytics endpoints"}
