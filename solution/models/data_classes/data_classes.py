from dataclasses import dataclass


# make success class
@dataclass
class Success:
    message: str = None
    response: dict = None
    status_code: int = None


# make error class
@dataclass
class Error:
    message: str = None
    status_code: int = None


@dataclass
class AzureSettings:
    token: str = None
    organization: str = None


@dataclass
class TelegramBotSettings:
    token: str = None
    chat_id: str = None
