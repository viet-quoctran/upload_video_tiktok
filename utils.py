from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from actions import wait_and_scroll_inside_element, double_click_like_and_click_close
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import settings as CONFIG
def random_scroll_and_select_video(driver, element_xpath):
    num_spaces = random.randint(3,7)
    for _ in range(num_spaces):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
        time.sleep(random.uniform(3,7))
    videos = driver.find_elements(By.XPATH, "//video")
    if videos:
        random.choice(videos).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element_xpath)))
        wait_and_scroll_inside_element(driver, element_xpath)
        double_click_like_and_click_close(driver, "//video", CONFIG.CLOSE_VIDEO)