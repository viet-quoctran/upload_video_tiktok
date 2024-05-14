from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from actions import wait_and_scroll_inside_element, double_click_like_and_click_close
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def random_scroll_and_select_video(driver, element_xpath, config):
    """Scrolls randomly on a webpage and selects a video to interact with.

    Args:
        driver (WebDriver): The Selenium WebDriver.
        element_xpath (str): The XPath to the element where interactions occur after selecting a video.
        config (dict): Configuration settings including keys like CLOSE_VIDEO for XPath.
    """
    num_spaces = random.randint(3, 5)
    for _ in range(num_spaces):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
        time.sleep(random.uniform(3, 7))
    
    videos = driver.find_elements(By.XPATH, "//video")
    if videos:
        chosen_video = random.choice(videos)
        chosen_video.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element_xpath)))
        wait_and_scroll_inside_element(driver, element_xpath)
        double_click_like_and_click_close(driver, "//video", config['CLOSE_VIDEO'])
    else:
        print("No videos found to interact with.")
