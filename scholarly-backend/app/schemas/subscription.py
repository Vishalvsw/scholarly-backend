from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class SubscriptionCreate(BaseModel):
    email: EmailStr

class SubscriptionResponse(BaseModel):
    id: str
    email: EmailStr
    subscribed_at: datetime
    is_active: bool
    unsubscribed_at: Optional[datetime] = None