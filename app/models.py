from pydantic import BaseModel, Field, field_validator
from typing import Optional

class HealthData(BaseModel):
    """Audits health indicators using strict data contracts."""
    year: int = Field(alias="date")
    value: Optional[float]
    
    @field_validator('year', mode='before')
    @classmethod
    def validate_year(cls, v):
        if int(v) > 2026: 
            raise ValueError("Anomalous Data: Future year detected.")
        return int(v)

    @field_validator('value')
    @classmethod
    def check_value(cls, v):
        if v is not None and v < 0: 
            raise ValueError("Integrity Error: Negative health expenditure.")
        return v