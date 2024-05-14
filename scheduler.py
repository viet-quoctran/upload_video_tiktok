import schedule
import time
import subprocess
import sys
import settings

def job(path_main, group_name):
    """Run the main script for the scheduled group."""
    try:
        subprocess.run(["python", path_main, group_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute the script: {e}")

def main(group_name):
    """Setup scheduled jobs for a specific group specified in settings.json."""
    config = settings.load_settings()
    group_config = config['groups'].get(group_name, None)
    
    if not group_config:
        print(f"No configuration found for group {group_name}. Please check your settings.json.")
        return
    
    schedule_time = group_config.get('SCHEDULE_TIME')
    path_main = group_config.get('PATH_MAIN')
    
    if schedule_time and path_main:
        # Schedule the job
        schedule.every().day.at(schedule_time).do(job, path_main=path_main, group_name=group_name)
        print(f"Scheduled to run every day at {schedule_time} for group {group_name}.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        print(f"Schedule time or path to main script not set for group {group_name}.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("No group name specified. Please provide a group name as an argument.")
