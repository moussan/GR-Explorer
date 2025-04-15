from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class CalculationBase(BaseModel):
    metric_name: str
    calculation_type: str
    input_parameters: Dict[str, Any]

class CalculationCreate(CalculationBase):
    pass

class Calculation(CalculationBase):
    id: int
    result: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 