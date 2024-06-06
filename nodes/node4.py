import asyncio
import websockets
import json

async def send_message():
    async with websockets.connect('ws://localhost:8764') as websocket:
        message = {
            "node": "Node 4",
            "message": "Hello from Node 4"
        }
        await websocket.send(json.dumps(message))

async def receive_message(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        print(f"Node 4 received: {data['message']} from {data['node']}")

async def main():
    server = await websockets.serve(receive_message, "localhost", 8764)
    await send_message()
    await server.wait_closed()

asyncio.run(main())
