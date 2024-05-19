import json
import os

class ConfigManager:
    def __init__(self, config_file='settings.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as config_file:
                return json.load(config_file)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save_config(self):
        try:
            with open(self.config_file, 'w') as config_file:
                json.dump(self.config, config_file, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_video_counts(self, group, profile_id, video_folder):
        profile_video_path = os.path.join(video_folder, profile_id)
        if os.path.exists(profile_video_path):
            uploaded_videos = len([f for f in os.listdir(profile_video_path) if f.endswith('_done.mp4')])
            total_videos = len([f for f in os.listdir(profile_video_path) if f.endswith('.mp4')])
            error_videos = len([f for f in os.listdir(profile_video_path) if f.endswith('_error.mp4')])
            remaining_videos = total_videos - uploaded_videos - error_videos
        else:
            uploaded_videos = 0
            remaining_videos = 0
            error_videos = 0

        self.config['groups'][group]['PROFILE_ID'][profile_id]['videos_uploaded'] = uploaded_videos
        self.config['groups'][group]['PROFILE_ID'][profile_id]['videos_remaining'] = remaining_videos
        self.config['groups'][group]['PROFILE_ID'][profile_id]['videos_error'] = error_videos
        self.save_config()

