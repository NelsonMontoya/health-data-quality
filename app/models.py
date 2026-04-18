from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

todays_year = datetime.now().year

class HealthData(BaseModel):
    """Universal model for auditing World Bank time-series data."""
    year: int = Field(alias="date")
    value: Optional[float]
    
    @field_validator('year', mode='before')
    @classmethod
    def validate_year(cls, v):
        # We are in 2026, so data shouldn't exist for 2027+
        if int(v) > todays_year: 
            raise ValueError("Anomalous Year: Data points cannot be in the future.")
        return int(v)

    @field_validator('value')
    @classmethod
    def check_value(cls, v):
        # Most indicators shouldn't be negative (Expenditure, GDP, CO2)
        if v is not None and v < 0: 
            raise ValueError("Integrity Error: Negative value detected.")
        return v