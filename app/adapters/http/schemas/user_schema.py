from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.value_objects.user_role import UserRole


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}