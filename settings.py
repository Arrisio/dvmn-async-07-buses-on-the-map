import sys
from typing import Optional, Union

from pydantic import BaseSettings, AnyUrl


class ServerSettings(BaseSettings):
    SEND_TO_BROWSER_INTERVAL: Union[int, float] = 1
    LOG_LEVEL: str = "INFO"
    class Config:
        env_file: str = ".env"
        env_file_encoding = "utf-8"

class FakeBusSettings(BaseSettings):
    SERVER_URL: AnyUrl = "ws://127.0.0.1:8080"
    CONNECTION_COUNT: int = 20

    BUS_COUNT: int = 1000

    BUS_MOVEMENT_COOLDOWN: Union[int, float] = 1
    MAX_BUFFER_SIZE: int = 100
    RECONNECT_TIMEOUT: int = 2

    ROUTES_FATH: str = "./routes"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file: str = ".env"
        env_file_encoding = "utf-8"



def get_loguru_config(log_level=ServerSettings().LOG_LEVEL)-> dict:
    return {
        "handlers": [
            {
                "sink": sys.stdout,
                "level": log_level,
                "format": "<level>{level: <8} {time:YYYY-MM-DD HH:mm:ss}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level> |{extra}",
            },
        ],
    }
