from app.models import HealthData

# 1. Simulemos un dato CORRECTO
try:
    dato_bueno = {
        "countryiso3code": "CAN",
        "date": "2024",
        "value": 11.5,
        "indicator_value": "Health Expenditure"
    }
    auditado = HealthData(**dato_bueno)
    print("✅ Prueba 1: Dato correcto pasó la auditoría.")
except Exception as e:
    print(f"❌ Prueba 1 falló inesperadamente: {e}")

# 2. Simulemos un dato CORRUPTO (Gasto negativo)
try:
    dato_malo = {
        "countryiso3code": "BRA",
        "date": "2024",
        "value": -5.0, # <--- ESTO DEBE FALLAR
        "indicator_value": "Health Expenditure"
    }
    HealthData(**dato_malo)
except Exception as e:
    print(f"✅ Prueba 2: El auditor detectó el error lógico correctamente: {e}")