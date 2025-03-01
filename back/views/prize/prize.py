from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from back.models.enums import PrizeType

class PrizeOut(BaseModel):
    prize_type: PrizeType
    expires_at: Optional[str] = None

class PrizeOutAddUUID(BaseModel):
    prize_uuid: UUID
    prize_type: PrizeType
    expires_at: Optional[str] = None
