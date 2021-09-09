from loguru import logger
import trio
from trio_websocket import open_websocket_url
from settings import FakeBusSettings

async def main():
    try:
        async with open_websocket_url(FakeBusSettings().SERVER_URL) as ws:
            await ws.send_message('"test": 1}')
            message = await ws.get_message()
            logger.info(f'Received message: {message}')

    except OSError as ose:
        logger.error('Connection attempt failed: %s', ose)


if __name__ == '__main__':
    trio.run(main)
