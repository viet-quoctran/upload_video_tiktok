from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def wait_and_scroll_inside_element(driver, element_xpath):
    """Wait for a few seconds and then perform a smooth scrolling inside a specific element."""
    time.sleep(random.uniform(5, 7))
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element_xpath)))
    total_scroll_distance = random.randint(200, 800)
    driver.execute_script(f"arguments[0].scrollTop += {total_scroll_distance}", element)

def double_click_like_and_click_close(driver, video_xpath, button_xpath):
    """Double-click on a video element and then click the close button."""
    video_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, video_xpath)))
    actions = ActionChains(driver)
    actions.double_click(video_element).perform()
    time.sleep(random.uniform(2, 3))
    close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    close_button.click()
