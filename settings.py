import json
import logging
import sys
import io
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def configure_stdout():
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='ignore')
    return sys.stdout
def load_settings():
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
            logging.info("Settings loaded successfully.")
            return settings
    except FileNotFoundError:
        logging.error("Settings file not found, loading default settings.")
        return {}  # Return an empty dict or default settings if needed
    except json.JSONDecodeError:
        logging.error("Error decoding the settings file.")
        return {}  # Return an empty dict or default settings if needed

def save_settings(settings):
    try:
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)
            logging.info("Settings saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")