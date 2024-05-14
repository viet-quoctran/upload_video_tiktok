import requests

class GPMLoginApiV3:
    def __init__(self, api_url, start_endpoint, close_endpoint):
        self.api_url = api_url
        self.start_endpoint = start_endpoint
        self.close_endpoint = close_endpoint
    def start_profile(self, profile_id):
        url = f"{self.api_url}{self.start_endpoint.format(id=profile_id)}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to start profile with ID {profile_id}: {response.status_code} {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def close_profile(self, profile_id):
        url = f"{self.api_url}{self.close_endpoint.format(id=profile_id)}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to close profile with ID {profile_id}: {response.status_code} {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
