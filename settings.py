import json
import logging
import sys
import io
import requests
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

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Telegram: {e}")

BOT_TOKEN = '6724583259:AAGQPd2ZRT8EpxMxt0eYd-VRf_IRUz7t5co'  # Suggest to use an environment variable or config
ID_TELEGRAM = '5370935211'  # Your chat ID or group ID
MESSAGE = "Hello, this is a test message!"