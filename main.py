import json

import trio
from trio_websocket import serve_websocket, ConnectionClosed


async def echo_server(request):
    ws = await request.accept()

    with open('156.json',  'r', encoding='utf-8') as fp:
        bus_data = json.load(fp)
    for lat, lng in bus_data['coordinates']:
        try:
            await ws.get_message()
            message =json.dumps(
                {
                    "msgType": "Buses",
                    "buses": [
                        {"busId": "c790сс", "lat": lat, "lng":lng,
                         "route": "120"},
                    ]
                }

            )
            print(message)
            await ws.send_message(message)
            # await trio.sleep(.1)
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(echo_server, "127.0.0.1", 8000, ssl_context=None)


trio.run(main)
