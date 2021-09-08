import json
import os
from itertools import cycle, islice
from random import choice, randint
from uuid import uuid4

import trio
from loguru import logger
from tenacity import (
    retry,
    wait_fixed,
    retry_if_exception_type,
    after_log,
)
from trio import MemorySendChannel, MemoryReceiveChannel
from trio_websocket import (
    open_websocket_url,
    HandshakeError,
    ConnectionClosed,
)

from server import Bus
from settings import FakeBusSettings, loguru_config


def load_routes(directory_path="routes"):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, "r", encoding="utf8") as file:
                yield json.load(file)


class FakeGate:
    def __init__(self, url: str):
        self.url = url
        self.send_channel: MemorySendChannel
        self.receive_channel: MemoryReceiveChannel
        self.send_channel, self.receive_channel = trio.open_memory_channel(
            FakeBusSettings().MAX_BUFFER_SIZE
        )

    @retry(
        wait=wait_fixed(FakeBusSettings().RECONNECT_TIMEOUT),
        sleep=trio.sleep,
        retry=retry_if_exception_type((HandshakeError, ConnectionClosed)),
        after=after_log(logger, FakeBusSettings().LOG_LEVEL),
    )
    async def send_updates(self):
        async with open_websocket_url(self.url) as ws:
            bus: Bus
            async for bus in self.receive_channel:
                await ws.send_message(bus.to_json())
                logger.debug(
                    "bus sent successfully", bus_id=bus.bus_id, route=bus.route
                )


class FakeBus:
    def __init__(self, route, gate: FakeGate):
        self.bus_id = uuid4()
        self.route = route
        self.gate = gate

        start_route_position = randint(0, len(route["coordinates"]) - 1)

        self.lat, self.lng = route["coordinates"][start_route_position]
        self._bus_coordinates = islice(
            cycle(self.route["coordinates"]),
            start_route_position,
            None,
        )

    async def emulate(self):
        while True:
            lat, lng = next(self._bus_coordinates)
            await self.gate.send_channel.send(
                Bus(
                    route=self.route["name"],
                    bus_id=self.bus_id,
                    lng=lng,
                    lat=lat,
                )
            )
            await trio.sleep(FakeBusSettings().BUS_MOVEMENT_INTERVAL)


async def main():
    connection_number = 10
    buses_number = 1000

    routes = list(load_routes("./routes"))
    gates = [FakeGate("ws://127.0.0.1:8080") for _ in range(connection_number)]
    buses = [
        FakeBus(route=choice(routes), gate=choice(gates))
        for _ in range(buses_number)
    ]
    logger.info('start simulation buses')
    async with trio.open_nursery() as nursery:
        for gate in gates:
            nursery.start_soon(gate.send_updates)
        for bus in buses:
            nursery.start_soon(bus.emulate)

if __name__ == '__main__':
    logger.configure(**loguru_config)
    try:
        trio.run(main)
    except KeyboardInterrupt:
        logger.info('Application closed.')

