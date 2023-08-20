import httpx
from configparser import ConfigParser


class TelegramBot:
    _instance = None

    def __init__(self):
        config = ConfigParser()
        config.read("../solution/settings.init")

        if "telegram_bot_token" in config["DEFAULT"] and \
                "telegram_chat_id" in config["DEFAULT"]:
            self.token = config["DEFAULT"]["telegram_bot_token"]
            self.chat_id = config["DEFAULT"]["telegram_chat_id"]

    @staticmethod
    def get_instance():
        if TelegramBot._instance is None:
            TelegramBot._instance = TelegramBot()

        return TelegramBot._instance

    def send_message(self, message: str):
        if not isinstance(message, str):
            raise ValueError("message must be string")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message
        }

        with httpx.Client() as client:
            response = client.post(url, json=data)

        if response.status_code == 200:
            return True
        else:
            raise False
