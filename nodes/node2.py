import asyncio
import websockets
import json

async def send_message():
    async with websockets.connect('ws://localhost:8762') as websocket:
        message = {
            "node": "Node 2",
            "message": "Hello from Node 2"
        }
        await websocket.send(json.dumps(message))

async def receive_message(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        print(f"Node 2 received: {data['message']} from {data['node']}")

async def main():
    server = await websockets.serve(receive_message, "localhost", 8762)
    await send_message()
    await server.wait_closed()

asyncio.run(main())
