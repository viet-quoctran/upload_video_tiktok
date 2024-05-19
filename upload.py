import os
import time
import random
import settings as CONFIG
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from display.config_manager import ConfigManager  # Import ConfigManager

CONFIG.configure_stdout()

def group_and_sort_videos(directory):
    videos = [f for f in os.listdir(directory) if f.endswith('.mp4')]
    grouped_videos = {}
    for video in videos:
        base_name = '-'.join(video.split('-')[:-1])  # Group by base name
        if base_name not in grouped_videos:
            grouped_videos[base_name] = []
        grouped_videos[base_name].append(video)
    
    # Sort each group
    for base_name in grouped_videos:
        grouped_videos[base_name].sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))
    
    return grouped_videos

def setup_upload(driver, profile_id, group_config, config, group_name):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, config['UPLOAD_BUTTON_XPATH']))).click()
        time.sleep(2)
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        driver.switch_to.frame(iframe)

        video_path = os.path.join(group_config['FOLDER_VIDEO_BASE'], profile_id)
        grouped_videos = group_and_sort_videos(video_path)
        
        for base_name, videos in grouped_videos.items():
            for video in videos:
                file_path = os.path.join(video_path, video)
                file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, config['FILE_INPUT_XPATH'])))
                file_input.send_keys(file_path)
                wait_for_upload_complete(driver, file_path, config, profile_id, group_name)  # Pass profile_id and group_name
                
    except Exception as e:
        print(f"An error occurred during file upload: {e}")

def wait_for_upload_complete(driver, file_path, config, profile_id, group_name):
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

                checkbox = driver.find_element(By.XPATH, '//input[@role="switch"]')
                if not checkbox.is_selected():
                    checkbox.click()
                time.sleep(10)

                img_element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="jsx-179570572 flex"]/img[contains(@src, "data:image/svg+xml;base64") and @class="jsx-179570572 check-icon"]'))
                )
                if img_element:
                    while True:
                        try:
                            final_button.click()
                            WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located((By.XPATH, '/html/body/div[8]/div/div/div[3]/button[2]/div/div'))
                            ).click()
                            time.sleep(5)
                            try:
                                driver.switch_to.default_content()
                                iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
                                driver.switch_to.frame(iframe)
                                file_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, config['FILE_INPUT_XPATH']))
                                )
                                if file_input:
                                    rename_uploaded_file(file_path)
                                    update_video_counts(profile_id, group_name)  # Update video counts
                                    break 
                            except NoSuchElementException:
                                pass
                        except NoSuchElementException:
                            print("Retrying to click final button...")
                            time.sleep(300) 
                            continue  
                else:
                    base, ext = os.path.splitext(file_path)
                    new_file_path = f"{base}_error{ext}"
                    os.rename(file_path, new_file_path)
                    print(f"File renamed to {new_file_path} due to error.")
                break
            time.sleep(1)
        except NoSuchElementException:
            print("Progress element not found, retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"An unexpected error occurred while waiting for upload to complete: {e}")
            break

def rename_uploaded_file(file_path):
    base, ext = os.path.splitext(file_path)
    new_file_path = f"{base}_done{ext}"
    os.rename(file_path, new_file_path)
    print(f"File renamed to {new_file_path}")

def update_video_counts(profile_id, group_name):
    config_manager = ConfigManager()
    video_folder = config_manager.config['groups'][group_name]['FOLDER_VIDEO_BASE']
    config_manager.update_video_counts(profile_id, group_name, video_folder)
