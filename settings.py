import sys
from typing import Optional, Union

from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file: str = ".env"
        env_file_encoding = "utf-8"


class ServerSettings(BaseSettings):
    SEND_TO_BROWSER_INTERVAL: Union[int, float] = 1
    class Config:
        env_file: str = ".env"
        env_file_encoding = "utf-8"

class FakeBusSettings(BaseSettings):
    SERVER_URL: AnyUrl = "ws://127.0.0.1:8080"

    BUS_MOVEMENT_INTERVAL: Union[int, float] = 1
    MAX_BUFFER_SIZE: int = 100
    RECONNECT_TIMEOUT: int = 2

    class Config:
        env_file: str = ".env"
        env_file_encoding = "utf-8"



loguru_config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "level": FakeBusSettings().LOG_LEVEL,
            "format": "<level>{level: <8} {time:YYYY-MM-DD HH:mm:ss}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level> |{extra}",
        },
    ],
}
