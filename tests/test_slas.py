import pytest
import time
from app.client import WorldBankClient

class TestProductionSLAs:
    """
    Suite de pruebas automatizadas para garantizar el cumplimiento 
    de los niveles de servicio (SLAs) de los datos de salud.
    """
    
    @classmethod
    def setup_class(cls):
        cls.client = WorldBankClient()
        cls.indicator = "SH.XPD.CHEX.GD.ZS"

    def test_api_performance_sla(self):
        """SLA: La API debe responder en menos de 1.5 segundos para Canadá."""
        start_time = time.time()
        data = self.client.fetch_health_indicator("CAN", self.indicator)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"\n⏱️ Tiempo de respuesta: {duration:.2f}s")
        
        assert data is not None, "La API no respondió."
        assert duration < 1.5, f"Fallo de SLA: Respuesta muy lenta ({duration:.2f}s)"

    def test_data_completeness_sla(self):
        """SLA: Los datos de Brasil deben tener al menos un 70% de registros válidos."""
        data = self.client.fetch_health_indicator("BRA", self.indicator)
        
        # Calculamos el porcentaje de 'completitud'
        total_records = len(data)
        valid_records = sum(1 for r in data if r['value'] is not None)
        completeness = (valid_records / total_records) * 100
        
        print(f"\n📊 Completitud de datos (BRA): {completeness:.1f}%")
        
        assert completeness >= 70, f"Calidad insuficiente: {completeness:.1f}% de datos válidos."