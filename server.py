import json
import asyncclick as click
from functools import partial
from typing import Dict, Union
from uuid import UUID

from loguru import logger
import trio
from trio_websocket import (
    serve_websocket,
    ConnectionClosed,
    WebSocketConnection,
    HandshakeError,
)
from dataclasses import dataclass, replace
from dataclasses_json import dataclass_json, LetterCase
import humps


from settings import ServerSettings, get_loguru_config


@dataclass_json
@dataclass
class WindowBounds:
    south_lat: float = 55.72396823082795
    north_lat: float = 55.771166064828556
    west_lng: float = 37.552042007446296
    east_lng: float = 37.716836929321296

    def is_inside(self, lat, lng):
        if (self.north_lat > lat > self.south_lat) and (
            self.east_lng > lng > self.west_lng
        ):
            return 1
        else:
            return 0

    def update(self, south_lat, north_lat, west_lng, east_lng):
        self.south_lat = south_lat
        self.north_lat = north_lat
        self.west_lng = west_lng
        self.east_lng = east_lng


@dataclass_json
@dataclass
class Bus:
    route: str
    bus_id: Union[str, UUID]
    lat: float
    lng: float


buses: dict[str, Bus] = {}


async def receive_bus_info(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()
            bus = Bus.from_json(message)
            buses[bus.bus_id] = bus
        except ConnectionClosed:
            break


async def listen_browser(ws: WebSocketConnection, windows_bounds: WindowBounds):
    while True:
        message = await ws.get_message()
        logger.debug(message)
        browser_message_data = json.loads(message)
        if browser_message_data["msgType"] == "newBounds":
            windows_bounds.update(**browser_message_data["data"])


async def send_buses(ws: WebSocketConnection, windows_bounds: WindowBounds):
    while True:
        message = humps.camelize(
            json.dumps(
                {
                    "msg_type": "Buses",
                    "buses": [
                        bus.to_dict()
                        for bus in buses.values()
                        if windows_bounds.is_inside(lat=bus.lat, lng=bus.lng)
                    ],
                }
            )
        )
        await ws.send_message(message)
        logger.debug("send to browser", message=message)
        await trio.sleep(ServerSettings().SEND_TO_BROWSER_INTERVAL)


async def talk_to_browser(request):
    windows_bounds = WindowBounds()
    try:
        ws = await request.accept()
        async with trio.open_nursery() as nursery:
            nursery.start_soon(listen_browser, ws, windows_bounds)
            nursery.start_soon(send_buses, ws, windows_bounds)

    except ConnectionClosed:
        logger.info("browser connection lost")


@click.command()
@click.option("-p", "--bus_port", default=8080, help="Port for bus emulator.")
@click.option(
    "-b", "--browser_port", default=8000, help="Number of bus routes."
)
@click.option("-l", "--log_level", help="Verbosity.")
async def main(bus_port, browser_port, log_level):
    logger.configure(**get_loguru_config(log_level))
    async with trio.open_nursery() as nursery:
        nursery.start_soon(
            partial(
                serve_websocket,
                handler=receive_bus_info,
                host="127.0.0.1",
                port=bus_port,
                ssl_context=None,
            )
        )
        nursery.start_soon(
            partial(
                serve_websocket,
                handler=talk_to_browser,
                host="127.0.0.1",
                port=browser_port,
                ssl_context=None,
            )
        )


if __name__ == "__main__":
    logger.info("starting server..")
    try:
        trio.run(main)
    except KeyboardInterrupt:
        logger.info("server stopped")
