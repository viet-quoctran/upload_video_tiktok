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
    indexed_files = []
    for file in files:
        try:
            index = int(file.split('-')[-1].split('.')[0])
            indexed_files.append((index, file))
        except ValueError:
            continue 
    if not indexed_files:
        return None
    indexed_files.sort()
    return indexed_files[0][1]

def setup_upload(driver):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, CONFIG.UPLOAD_BUTTON_XPATH))).click()
        time.sleep(2)
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        driver.switch_to.frame(iframe)
        time.sleep(2)
        file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, CONFIG.FILE_INPUT_XPATH)))

        lowest_file = get_lowest_numbered_file(CONFIG.FOLDER_VIDEO)
        if lowest_file:
            file_path = os.path.join(CONFIG.FOLDER_VIDEO, lowest_file)
            time.sleep(random.uniform(5,9))
            file_input.send_keys(file_path)
            wait_for_upload_complete(driver,file_path)
        else:
            print("No suitable file found.") 
        time.sleep(10)

    except Exception as e:
        print(f"An error occurred: {e}")

def wait_for_upload_complete(driver,file_path):
    while True:
        try:
            progress_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, CONFIG.PROGRESS_XPATH))
            )
            progress_text = progress_element.text
            if progress_text == "100%":
                print("Upload completed successfully.")
                driver.switch_to.default_content()
                iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
                driver.switch_to.frame(iframe)
                final_button = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, CONFIG.FINAL_UPLOAD_BUTTON))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", final_button)
                time.sleep(random.uniform(2, 5))
                final_button.click()
                rename_uploaded_file(file_path)
                break
            time.sleep(1)

        except NoSuchElementException:
            print("Progress element not found, waiting...")
            time.sleep(1)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break 
def rename_uploaded_file(file_path):
    base, ext = os.path.splitext(file_path)
    new_file_path = f"{base}_done{ext}"
    os.rename(file_path, new_file_path)
    print(f"File renamed to {new_file_path}")
    