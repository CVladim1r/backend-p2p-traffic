
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field

class ReferralUserStats(BaseModel):
    uuid: str
    username: Optional[str]
    profile_photo: Optional[str]
    rating: Optional[float]
    is_vip: bool
    completed_buys_count: int
    total_buys_amount: Decimal
    completed_sales_count: int
    total_sales_amount: Decimal
    total_earned: Decimal = Field(..., description="Сумма заработанная от реферала")

class ReferralStatsOut(BaseModel):
    referrals: List[ReferralUserStats]