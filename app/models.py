from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

current_year = datetime.now().year

class Country(BaseModel):
    """Modelo para limpiar y validar la lista de países."""
    id: str
    name: str
    region: str

    @classmethod
    def from_api(cls, data):
        """Transforma el JSON complejo de la API en un objeto limpio."""
        return cls(
            id=data['id'],
            name=data['name'],
            region=data['region']['value']
        )

class HealthData(BaseModel):
    """Modelo para auditar los indicadores de salud."""
    country_iso: str = Field(alias="countryiso3code")
    year: int = Field(alias="date")
    value: Optional[float] # Puede ser None si el país no reportó ese año
    indicator_name: str = Field(alias="indicator_value")

    # --- REGLAS DE AUDITORÍA (BUSINESS LOGIC) ---

    @field_validator('year', mode='before')
    @classmethod
    def validate_year(cls, v):
        """Asegura que no estemos procesando datos del futuro."""
        year = int(v)
        if year > current_year:
            raise ValueError(f"Data Anomaly: El año {year} es inválido para {current_year}.")
        return year

    @field_validator('value')
    @classmethod
    def check_logical_value(cls, v):
        """Regla de Oro: El gasto en salud no puede ser negativo."""
        if v is not None and v < 0:
            raise ValueError("Integrity Error: Gasto negativo detectado.")
        return v