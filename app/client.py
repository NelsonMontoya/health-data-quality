import requests

class WorldBankClient:
    """
    Clase encargada de la comunicación técnica con la API del Banco Mundial.
    Implementa el 'Data Discovery' para evitar datos fijos (hardcoded).
    """
    BASE_URL = "https://api.worldbank.org/v2"

    def get_countries_list(self):
        """
        Paso de Discovery: Obtiene la lista de todos los países disponibles.
        Configurado para traer 300 registros para cubrir todo el globo.
        """
        url = f"{self.BASE_URL}/country?format=json&per_page=300"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Lanza error si la API falla (404, 500, etc.)
            
            # La API devuelve una lista: [Metadatos, Lista_de_Paises]
            data = response.json()
            return data[1] if len(data) > 1 else []
        except Exception as e:
            print(f"❌ Error al descubrir países: {e}")
            return []

    def fetch_health_indicator(self, country_iso: str, indicator: str = "SH.XPD.CHEX.GD.ZS"):
        """
        Paso de Ingestión: Descarga el indicador de salud para un país específico.
        Por defecto usa: Gasto corriente en salud (% del PIB).
        """
        url = f"{self.BASE_URL}/country/{country_iso}/indicator/{indicator}?format=json&per_page=50"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[1] if len(data) > 1 else []
        except Exception as e:
            print(f"❌ Error al descargar datos de {country_iso}: {e}")
            return []