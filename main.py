from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import settings
from api import GPMLoginApiV3
from utils import random_scroll_and_select_video
from upload import setup_upload
import random
import time

def setup_driver(profile_id, group_config, config):
    # Use the specific API URL and endpoints provided in the group_config
    api = GPMLoginApiV3(config['API_URL'], config['START_ENDPOINT'], config['CLOSE_ENDPOINT'])
    start_result = api.start_profile(profile_id)
    if start_result:
        options = Options()
        options.binary_location = start_result["data"]["browser_location"]
        options.add_experimental_option("debuggerAddress", f"localhost:{start_result['data']['remote_debugging_address'].split(':')[1]}")
        service = Service(executable_path=start_result["data"]["driver_path"])
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(config['URL_TIKTOK'])
        try:
            for _ in range(random.randint(1, 3)):
                random_scroll_and_select_video(driver, config['XPATH_COMMENT'], config)
                time.sleep(random.uniform(2, 5))
            setup_upload(driver, profile_id, group_config, config)
        finally:
            driver.quit()
            api.close_profile(profile_id)

def main(group_name):
    config = settings.load_settings()
    group_config = config['groups'].get(group_name)
    if group_config:
        profile_ids = group_config['PROFILE_ID']
        with ThreadPoolExecutor(max_workers=len(profile_ids)) as executor:
            for profile_id in profile_ids:
                executor.submit(setup_driver, profile_id, group_config, config)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("No group specified.")
