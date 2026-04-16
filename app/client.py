import requests

class WorldBankClient:
    """Handles professional communication with the World Bank API."""
    BASE_URL = "https://api.worldbank.org/v2"

    def get_countries_list(self):
        """Fetches the comprehensive list of global countries/regions."""
        url = f"{self.BASE_URL}/country?format=json&per_page=300"
        try:
            # We increased the timeout slightly to 15 seconds for stability
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()[1]
        except requests.exceptions.RequestException as e:
            print(f"Logging Error: Connection issue during Discovery. {e}")
            return []

    def fetch_health_indicator(self, country_iso: str):
        """Retrieves health expenditure as % of GDP for a specific nation."""
        indicator = "SH.XPD.CHEX.GD.ZS"
        url = f"{self.BASE_URL}/country/{country_iso}/indicator/{indicator}?format=json&per_page=50"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()[1]
        except requests.exceptions.Timeout:
            print("Logging Error: The World Bank API is taking too long to respond.")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Logging Error: {e}")
            return []