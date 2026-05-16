from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user), unread_only: bool = False):
    q = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc())
    if unread_only:
        q = q.filter(Notification.is_read == False)  # noqa: E712
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "event_type": n.event_type,
            "emergency_id": n.emergency_id,
            "is_read": n.is_read,
            "play_sound": n.play_sound,
            "created_at": n.created_at.isoformat(),
        }
        for n in q.limit(50).all()
    ]


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"ok": True}
