from typing import Optional, Union

from pydantic import BaseSettings


class FakeBusSettings(BaseSettings):
    BUS_MOVEMENT_INTERVAL: Union[int, float] = 1
    MAX_BUFFER_SIZE: int = 100
    RECONNECT_TIMEOUT: int = 2
    LOG_LEVEL: str = "INFO"
