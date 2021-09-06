import json
import os

import trio
from sys import stderr
from trio_websocket import open_websocket_url

def load_routes(directory_path='routes'):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)



async def main():
    try:
        async with open_websocket_url("ws://127.0.0.1:8080") as ws:
            for rout_data in load_routes():
                for lat, lng in rout_data['coordinates']:
                    bus_data = {
                        "busId": rout_data['name'],
                        "lat": lat,
                        "lng": lng,
                        "route": rout_data['name'],
                    }
                await ws.send_message(json.dumps(bus_data))
                # await trio.sleep(.1)
            # await ws.get_message()
    except OSError as ose:
        print("Connection attempt failed: %s" % ose, file=stderr)


trio.run(main)
