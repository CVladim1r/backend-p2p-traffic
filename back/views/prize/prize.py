from pydantic import BaseModel
from typing import Optional

class PrizeOut(BaseModel):
    prize_type: Optional[str] = None
    expires_at: Optional[str] = None