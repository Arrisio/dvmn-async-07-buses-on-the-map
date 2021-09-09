from loguru import logger
import trio
from trio_websocket import open_websocket_url


async def main():
    try:
        async with open_websocket_url("ws://127.0.0.1:8080") as ws:
            await ws.send_message('"{test": 1}')
            message = await ws.get_message()
            logger.info(f"Received message: {message}")

            await ws.send_message("some string")
            message = await ws.get_message()
            logger.info(f"Received message: {message}")

        async with open_websocket_url("ws://127.0.0.1:8000") as ws:
            await ws.send_message('"{test": 1}')
            message = await ws.get_message()
            logger.info(f"Received message: {message}")

            await ws.send_message("some string")
            message = await ws.get_message()
            logger.info(f"Received message: {message}")

    except OSError as ose:
        logger.error("Connection attempt failed: %s", ose)


if __name__ == "__main__":
    trio.run(main)
