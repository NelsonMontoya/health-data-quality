import requests

class WorldBankClient:
    BASE_URL = "https://api.worldbank.org/v2"

    def get_countries_list(self):
        url = f"{self.BASE_URL}/country?format=json&per_page=300"
        response = requests.get(url, timeout=10)
        return response.json()[1] if response.status_code == 200 else []

    def fetch_health_indicator(self, country_iso: str):
        indicator = "SH.XPD.CHEX.GD.ZS"
        url = f"{self.BASE_URL}/country/{country_iso}/indicator/{indicator}?format=json&per_page=50"
        response = requests.get(url, timeout=10)
        return response.json()[1] if response.status_code == 200 else []