import json
import sys
from functools import partial
from typing import Dict, Union
from uuid import UUID

from loguru import logger
import trio
from trio_websocket import serve_websocket, ConnectionClosed, WebSocketConnection, HandshakeError
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
import humps


# @dataclass_json (letter_case=LetterCase.CAMEL)
from settings import loguru_config, ServerSettings


@dataclass_json
@dataclass
class Bus:
    route: str
    bus_id: Union[str, UUID]
    lat: float
    lng: float


buses: dict[str,Bus] = {}


async def receive_bus_info(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()
            bus = Bus.from_json(message)
            # logger.debug(bus)
            buses[bus.bus_id] = bus
            # logger.debug('add bus', busses=buses)

        except ConnectionClosed:
            break



async def send_routes_to_browser(ws: WebSocketConnection ):
    while True:
        # await ws.get_message()

        message = humps.camelize(json.dumps(

            {
                "msg_type": "Buses",
                "buses": [bus.to_dict() for bus in buses.values()]
            }

        ))



        logger.debug('send to browser', message=message)
        await ws.send_message(message)
        await trio.sleep(ServerSettings().SEND_TO_BROWSER_INTERVAL)


async def talk_to_browser(request):
    ws = await request.accept()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(send_routes_to_browser, ws)




async def main():
    logger.configure(**loguru_config)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(
            partial(
                serve_websocket,
                handler=receive_bus_info,
                host="127.0.0.1",
                port=8080,
                ssl_context=None,
            )
        )
        nursery.start_soon(
            partial(
                serve_websocket,
                handler=talk_to_browser,
                host="127.0.0.1",
                port=8000,
                ssl_context=None,
            )
        )
        # await serve_websocket(echo_server, '127.0.0.1', 8080, ssl_context=None)


if __name__ == '__main__':
    logger.info('starting server..')
    try:
        trio.run(main)
    except KeyboardInterrupt:
        logger.info('server stopped')

