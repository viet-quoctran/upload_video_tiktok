import requests
import settings as CONFIG
class GPMLoginApiV3:
    def __init__(self, api_url):
        self.api_url = api_url

    def start_profile(self, profile_id):
        url = f"{self.api_url}{CONFIG.START_ENDPOINT}".replace("{id}", profile_id)
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    def close_profile(self, profile_id):
        url = f"{self.api_url}{CONFIG.CLOSE_ENDPOINT}".replace("{id}", profile_id)
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None