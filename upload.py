import os
import time
import random
import settings as CONFIG
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
CONFIG.configure_stdout()
def get_lowest_numbered_file(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.mp4')]
    indexed_files = [(int(f.split('-')[-1].split('.')[0]), f) for f in files if f.split('-')[-1].split('.')[0].isdigit()]
    return min(indexed_files, default=(None, None))[1] if indexed_files else None

def setup_upload(driver,profile_id, group_config, config):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, config['UPLOAD_BUTTON_XPATH']))).click()
        time.sleep(2)
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        driver.switch_to.frame(iframe)
        file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, config['FILE_INPUT_XPATH'])))
        video_path = os.path.join(group_config['FOLDER_VIDEO_BASE'], profile_id)
        lowest_file = get_lowest_numbered_file(video_path)
        if lowest_file:
            file_path = os.path.join(video_path, lowest_file)
            file_input.send_keys(file_path)
            wait_for_upload_complete(driver, file_path, config)
        else:
            message = "No more videos, please upload a new one"
            CONFIG.send_telegram_message(CONFIG.BOT_TOKEN, CONFIG.ID_TELEGRAM, message)
    except Exception as e:
        print(f"An error occurred during file upload: {e}")

def wait_for_upload_complete(driver, file_path, config):
    while True:
        try:
            progress_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, config['PROGRESS_XPATH']))
            )
            if "100%" in progress_element.text:
                driver.switch_to.default_content()
                iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
                driver.switch_to.frame(iframe)
                final_button = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, config['FINAL_UPLOAD_BUTTON']))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", final_button)
                time.sleep(random.uniform(2, 5))
                final_button.click()
                rename_uploaded_file(file_path)
                break
            time.sleep(1)
        except NoSuchElementException:
            print("Progress element not found, retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"An unexpected error occurred while waiting for upload to complete: {e}")
            break
    rename_uploaded_file(file_path)

def rename_uploaded_file(file_path):
    base, ext = os.path.splitext(file_path)
    new_file_path = f"{base}_done{ext}"
    os.rename(file_path, new_file_path)
    print(f"File renamed to {new_file_path}")
