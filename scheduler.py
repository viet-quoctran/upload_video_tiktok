import schedule
import time
import subprocess
import settings as CONFIG

def job():
    subprocess.run(["python", "E:/upload_channel/main.py"])

schedule.every().day.at(CONFIG.SCHEDULE_TIME).do(job)

while True:
    schedule.run_pending()
    time.sleep(60) 