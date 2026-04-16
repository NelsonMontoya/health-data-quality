import pytest
import time
from app.client import WorldBankClient

def test_api_performance_sla():
    """SLA: API must respond in under 2.0 seconds for production readiness."""
    client = WorldBankClient()
    start = time.time()
    client.fetch_health_indicator("CAN")
    duration = time.time() - start
    print(f"\n⏱️ Latency: {duration:.2f}s")
    assert duration < 2.0

def test_data_completeness_sla():
    """SLA: Data source must provide a minimum threshold of usable records."""
    client = WorldBankClient()
    data = client.fetch_health_indicator("BRA")
    valid = sum(1 for r in data if r['value'] is not None)
    completeness = (valid / len(data)) * 100
    print(f"\n📊 Completeness Score: {completeness:.1f}%")
    assert completeness > 40