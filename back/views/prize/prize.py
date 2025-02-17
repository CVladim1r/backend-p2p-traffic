from pydantic import BaseModel
from typing import Optional

from back.models.enums import PrizeType

class PrizeOut(BaseModel):
    prize_type: PrizeType
    expires_at: Optional[str] = None
