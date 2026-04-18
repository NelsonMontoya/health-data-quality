import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class WorldBankClient:
    """Resilient API Client with Automated Retries and Data Validation."""
    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self):
        self.session = requests.Session()
        # Professional Retry Strategy: 3 attempts with exponential backoff
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_countries_list(self):
        """Fetches all countries, handling potential API structural errors."""
        url = f"{self.BASE_URL}/country?format=json&per_page=300"
        try:
            response = self.session.get(url, timeout=20)
            data = response.json()
            # Defensive check: Ensure response is a list and has data at index 1
            if isinstance(data, list) and len(data) > 1:
                return data[1]
            return []
        except Exception as e:
            print(f"Discovery Error: {e}")
            return []

    def fetch_indicator(self, country_iso: str, indicator_code: str):
        """Universal fetcher with a 30s timeout and structural validation."""
        url = f"{self.BASE_URL}/country/{country_iso}/indicator/{indicator_code}?format=json&per_page=50"
        try:
            # Increased timeout for complex indicators like CO2
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"⚠️ API Warning: {response.status_code} for {country_iso}")
                return []

            data_json = response.json()

            # CRITICAL: Verify the API returned [metadata, data_list]
            if isinstance(data_json, list) and len(data_json) >= 2:
                return data_json[1]
            
            # If the API returns an error message instead of data
            print(f"🚫 No data or structural error from API for {country_iso}")
            return []

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout Error: World Bank server is too slow for {indicator_code}")
            return []
        except Exception as e:
            print(f"❌ Unexpected Connection Error: {e}")
            return []