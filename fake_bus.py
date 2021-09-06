import json
import os
from itertools import cycle

import trio
from sys import stderr
from trio_websocket import open_websocket_url

def load_routes(directory_path='routes'):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)


async def run_bus(url, route):
    async with open_websocket_url(url) as ws:
        for lat, lng in cycle(route['coordinates']):
            bus_data = {
                "busId": route['name'],
                "lat": lat,
                "lng": lng,
                "route": route['name'],
            }
            await ws.send_message(json.dumps(bus_data, ensure_ascii=False))


async def main():
    try:

        for route in load_routes():
            async with trio.open_nursery() as nursery:
                nursery.start_soon(run_bus, "ws://127.0.0.1:8080", route)

                # await trio.sleep(.1)
            # await ws.get_message()
    except OSError as ose:
        print("Connection attempt failed: %s" % ose, file=stderr)


trio.run(main)
