from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional

class Loan(BaseModel):
    maturity_date: date
    reference_rate: str
    rate_floor: Decimal
    rate_ceiling: Decimal
    rate_spread: Decimal
    months: Optional[int] = 1

class FloatingRate(BaseModel):
    date: date
    rate: Decimal