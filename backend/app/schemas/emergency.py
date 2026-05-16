from datetime import datetime

from pydantic import BaseModel, Field

from app.models.emergency import EmergencyStatus, EmergencyType, SeverityLevel


class EmergencyCreate(BaseModel):
    reporter_name: str
    reporter_phone: str
    emergency_type: EmergencyType
    severity: SeverityLevel
    lat: float
    lng: float
    notes: str | None = None


class EmergencyUpdate(BaseModel):
    status: EmergencyStatus | None = None
    ambulance_id: int | None = None
    hospital_id: int | None = None


class EmergencyOut(BaseModel):
    id: int
    reporter_name: str
    reporter_phone: str
    emergency_type: EmergencyType
    severity: SeverityLevel
    lat: float
    lng: float
    notes: str | None
    status: EmergencyStatus
    ambulance_id: int | None
    hospital_id: int | None
    eta_minutes: float | None
    route_polyline: str | None
    priority_score: int
    auto_assigned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignRequest(BaseModel):
    ambulance_id: int | None = None
    hospital_id: int | None = None
    override: bool = False
