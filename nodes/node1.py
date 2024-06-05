import asyncio
import websockets
import json
import time

async def send_message():
    await asyncio.sleep(2)  # Wait for Node 2 server to start
    async with websockets.connect('ws://localhost:8762') as websocket:
        message = {
            "node": "Node 1",
            "message": "Hello from Node 1"
        }
        await websocket.send(json.dumps(message))

async def receive_message(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        print(f"Node 1 received: {data['message']} from {data['node']}")

async def main():
    server = await websockets.serve(receive_message, "localhost", 8761)
    await asyncio.gather(server.wait_closed(), send_message())

asyncio.run(main())
