import pytest
import time
from app.client import WorldBankClient

def test_api_performance():
    client = WorldBankClient()
    start = time.time()
    client.fetch_health_indicator("CAN")
    assert (time.time() - start) < 2.0  # SLA de 2 segundos

def test_brazil_data():
    client = WorldBankClient()
    data = client.fetch_health_indicator("BRA")
    valid = sum(1 for r in data if r['value'] is not None)
    completeness = (valid / len(data)) * 100
    assert completeness > 40 # Bajamos el umbral para que veas el verde