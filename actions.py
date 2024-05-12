from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def wait_and_scroll_inside_element(driver, element_xpath):
    time.sleep(random.uniform(5,7))
    element = driver.find_element(By.XPATH, element_xpath)
    for _ in range(random.randint(4, 8)):
        scroll_distance = random.randint(20, 100)
        for step in range(15):
            single_scroll = random.randint(1, scroll_distance // 15 + 1)
            driver.execute_script(f"arguments[0].scrollTop += {single_scroll}", element)
            time.sleep(0.005)
        time.sleep(random.uniform(2, 3))

def double_click_like_and_click_close(driver, video_xpath, button_xpath):
    video_element = driver.find_element(By.XPATH, video_xpath)
    actions = ActionChains(driver)
    actions.double_click(video_element).perform()
    time.sleep(random.uniform(2,3))
    close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
    close_button.click()