from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from api import GPMLoginApiV3
from utils import random_scroll_and_select_video
from upload import setup_upload
import random
import time
import settings as CONFIG
def setup_driver(start_result):
    options = Options()
    options.binary_location = start_result["data"]["browser_location"]
    options.add_experimental_option("debuggerAddress", f"localhost:{start_result['data']['remote_debugging_address'].split(':')[1]}")
    service = Service(executable_path=start_result["data"]["driver_path"])
    return webdriver.Chrome(service=service, options=options)

def main():
    api = GPMLoginApiV3(CONFIG.API_URL)
    start_result = api.start_profile(CONFIG.PROFILE_ID)
    if start_result:
        driver = setup_driver(start_result)
        driver.get(CONFIG.URL_TIKTOK)
        try:
            for _ in range(random.randint(1, 3)):
                random_scroll_and_select_video(driver, CONFIG.XPATH_COMMENT)
                time.sleep(random.uniform(2, 5))
            setup_upload(driver)
        finally:
            driver.quit()
            api.close_profile(CONFIG.PROFILE_ID)

if __name__ == "__main__":
    main()