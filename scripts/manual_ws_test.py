import asyncio
import json
import websockets


async def main():
    uri = "ws://127.0.0.1:8000/ws/process"

    async with websockets.connect(uri) as websocket:
        set_payload = {
            "source": "client_1",
            "payload": {
                "operation": "set_value",
                "resource_id": "sensor_01",
                "value": 42,
            },
        }

        get_payload = {
            "source": "client_1",
            "payload": {
                "operation": "get_value",
                "resource_id": "sensor_01",
            },
        }

        await websocket.send(json.dumps(set_payload))
        set_response = await websocket.recv()
        print("SET RESPONSE:")
        print(set_response)

        await websocket.send(json.dumps(get_payload))
        get_response = await websocket.recv()
        print("GET RESPONSE:")
        print(get_response)


if __name__ == "__main__":
    asyncio.run(main())