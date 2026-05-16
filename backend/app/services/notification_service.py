from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User, UserRole
from app.websocket.manager import manager


async def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    event_type: str,
    emergency_id: int | None = None,
    play_sound: bool = False,
    broadcast_channel: str | None = None,
):
    n = Notification(
        user_id=user_id,
        title=title,
        message=message,
        event_type=event_type,
        emergency_id=emergency_id,
        play_sound=play_sound,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    payload = {
        "type": "notification",
        "id": n.id,
        "title": title,
        "message": message,
        "event_type": event_type,
        "emergency_id": emergency_id,
        "play_sound": play_sound,
    }
    await manager.send_user(user_id, payload)
    if broadcast_channel:
        await manager.broadcast(payload, broadcast_channel)
    return n


async def notify_role(
    db: Session,
    role: UserRole,
    title: str,
    message: str,
    event_type: str,
    emergency_id: int | None = None,
    play_sound: bool = False,
):
    users = db.query(User).filter(User.role == role, User.is_active == True).all()  # noqa: E712
    for u in users:
        await create_notification(db, u.id, title, message, event_type, emergency_id, play_sound)
    channel = role.value if role != UserRole.ADMIN else "dispatcher"
    await manager.broadcast(
        {"type": "notification", "title": title, "message": message, "event_type": event_type, "play_sound": play_sound},
        channel if role != UserRole.ADMIN else "dispatcher",
    )
