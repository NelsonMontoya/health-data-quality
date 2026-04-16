import pytest
import time
from app.client import WorldBankClient

class TestProductionSLAs:
    """
    Automated test suite to enforce Service Level Agreements (SLAs) 
    and Data Quality Gates.
    """
    
    @classmethod
    def setup_class(cls):
        cls.client = WorldBankClient()

    def test_api_performance_sla(self):
        """SLA: API must respond in under 2.0 seconds for production readiness."""
        start = time.time()
        self.client.fetch_health_indicator("CAN")
        duration = time.time() - start
        
        print(f"\n⏱️ Latency Check: {duration:.2f}s")
        assert duration < 2.0, f"Performance SLA Failure: {duration:.2f}s is too slow."

    def test_data_completeness_sla(self):
        """
        STRICT SLA: Data source must provide at least 80% usable records 
        to pass the Production Quality Gate.
        """
        # Testing with Brazil as a known baseline for sparse data
        data = self.client.fetch_health_indicator("BRA")
        
        if not data:
            pytest.fail("Network Timeout: Could not retrieve data for audit.")

        total_records = len(data)
        valid_records = sum(1 for r in data if r['value'] is not None)
        completeness = (valid_records / total_records) * 100
        
        print(f"\n📊 Integrity Audit Score: {completeness:.1f}%")
        
        # Enforcing the 80% Threshold
        assert completeness >= 80, (
            f"Quality Gate Failed! Data completeness is only {completeness:.1f}%, "
            f"which is below the required 80% threshold."
        )