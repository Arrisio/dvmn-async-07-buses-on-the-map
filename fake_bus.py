import json

import trio
from sys import stderr
from trio_websocket import open_websocket_url


async def main():
    try:
        async with open_websocket_url("ws://127.0.0.1:8080") as ws:
            while True:
                bus_data = {
                    "busId": "c790сс",
                    "lat": 55.747629944737,
                    "lng": 37.641726387317,
                    "route": "156",
                }
                await ws.send_message(json.dumps(bus_data))
                await trio.sleep(.1)
            # await ws.get_message()
    except OSError as ose:
        print("Connection attempt failed: %s" % ose, file=stderr)


trio.run(main)
