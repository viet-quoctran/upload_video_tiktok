import os
import time
import random
import settings as CONFIG
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from display.config_manager import ConfigManager  # Import ConfigManager

CONFIG.configure_stdout()

def group_and_sort_videos(directory):
    videos = [f for f in os.listdir(directory) if f.endswith('.mp4') and '_error' not in f]
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
        upload_count = group_config['PROFILE_ID'][profile_id].get('upload_count', 1)
        upload_videos(driver, grouped_videos, upload_count, video_path, config, profile_id, group_name)
                
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
                            modal_element = WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="TUXModal common-modal common-modal-width--medium common-modal-confirm-modal"]'))
                            )
                            if modal_element:
                                cancel_button = modal_element.find_element(By.XPATH, '//div[@class="TUXModal common-modal common-modal-width--medium common-modal-confirm-modal"]//button[contains(@class, "TUXButton--secondary") and @type="button"]')
                                cancel_button.click()
                                time.sleep(5)
                                
                                current_url = driver.current_url
                                if current_url == "https://www.tiktok.com/tiktokstudio/content":
                                    delete_uploaded_file(file_path, profile_id, group_name)  # Ensure correct call
                                    driver.get(config['URL_UPLOAD'])
                                    time.sleep(5)
                                    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
                                    driver.switch_to.frame(iframe)
                                    return True  # Indicate the page was refreshed and continue uploading
                                else:
                                    return False  # Indicate the upload failed
                            else:
                                return False  # Indicate the upload failed
                        
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
    return False  # Indicate the upload completed successfully without needing a refresh

def delete_uploaded_file(file_path, profile_id, group_name):
    try:
        os.remove(file_path)
        print(f"File {file_path} deleted successfully.")
        # Cập nhật số lượng video đã tải lên trong settings.json
        config_manager = ConfigManager()
        config_manager.reload_config()
        config = config_manager.config
        config['groups'][group_name]['PROFILE_ID'][profile_id]['videos_uploaded'] += 1
        config_manager.save_config()
    except Exception as e:
        print(f"Failed to delete file {file_path}: {e}")

def update_video_counts(profile_id, group_name):
    config_manager = ConfigManager()
    config_manager.reload_config()
    video_folder = config_manager.config['groups'][group_name]['FOLDER_VIDEO_BASE']
    config_manager.update_video_counts(group_name, profile_id, video_folder)

def upload_videos(driver, grouped_videos, upload_count, video_path, config, profile_id, group_name):
    total_uploaded = 0  # Track total number of videos uploaded
    for base_name, videos in grouped_videos.items():
        i = 0
        while i < len(videos):
            if total_uploaded >= upload_count:
                return False  # Indicate the upload failed
            video = videos[i]
            file_path = os.path.join(video_path, video)
            file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, config['FILE_INPUT_XPATH'])))
            file_input.send_keys(file_path)
            if not wait_for_upload_complete(driver, file_path, config, profile_id, group_name):
                return  # Exit if the upload fails or needs to refresh the page
            total_uploaded += 1  # Increment the total uploaded count
            i += 1
