import sys
import io

def configure_stdout():
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='ignore')
    return sys.stdout

# Những mục cần config
# Hẹn giờ 
SCHEDULE_TIME = '17:02' 
# Path file cần chạy ở đây
PATH_MAIN = "E:/upload_channel/main.py"
# ID của profile
PROFILE_ID = "c7190a4d-d94d-402f-8823-1784e54e45f9"
# FOLDER chứa video
FOLDER_VIDEO = "E:\\upload_channel\\video1"






START_ENDPOINT = "/api/v3/profiles/start/{id}"
CLOSE_ENDPOINT = "/api/v3/profiles/close/{id}"
API_URL = "http://127.0.0.1:19995"


# main.py
URL_TIKTOK = "https://www.tiktok.com/"
XPATH_COMMENT = "/html/body/div[1]/div[2]/div[4]/div/div[2]/div[1]/div"

# upload.py
UPLOAD_BUTTON_XPATH = "/html/body/div[1]/div[1]/div/div[3]/div[1]"
FILE_INPUT_XPATH = "//input[@type='file']"

PROGRESS_XPATH = "/html/body/div[1]/div/div/div/div[1]/div[3]/div"
FINAL_UPLOAD_BUTTON = "/html/body/div[1]/div/div/div/div[2]/div/div[2]/div[8]/button[2]"

# utils.py
CLOSE_VIDEO = "/html/body/div[1]/div[2]/div[4]/div/div[1]/button[1]"