import httpx
from configparser import ConfigParser

from solution.data_classes.data_classes import Success, Error, TelegramBotSettings


class TelegramBot:

    def __init__(self, settings: dict = None):
        config = ConfigParser()
        config.read("../solution/settings.init")

        if "telegram_bot_token" in config["DEFAULT"] and \
                "telegram_chat_id" in config["DEFAULT"]:
            self.settings = TelegramBotSettings(config["DEFAULT"]["telegram_bot_token"],
                                                config["DEFAULT"]["telegram_chat_id"])

        if settings and "telegram_bot_token" in settings and "telegram_chat_id" in settings:
            self.settings = TelegramBotSettings(settings["telegram_bot_token"],
                                                settings["telegram_chat_id"])
        if not self.settings:
            raise ValueError("Telegram bot settings not found.")

    def send_message(self, message: str):
        if not isinstance(message, str):
            raise ValueError("message must be string")

        url = f"https://api.telegram.org/bot{self.settings.token}/sendMessage"
        data = {
            "chat_id": self.settings.chat_id,
            "text": message
        }

        with httpx.Client() as client:
            response = client.post(url, json=data)

            if response.status_code == 200:
                return Success(message="Message sent successfully.")
            else:
                return Error(message="Error occurred while sending message.")
