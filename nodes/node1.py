import asyncio
import websockets
import json
import aiomysql

async def start_db_pool():
    return await aiomysql.create_pool(
        host='localhost', port=3306,
        user='root', password='Meet@123',
        db='library', charset='utf8',
        autocommit=True)

async def send_initial_message():
    # Simulating an initial message sent to Node 1 from a client
    await asyncio.sleep(2)
    async with websockets.connect('ws://localhost:8761') as websocket:
        message = {
            "type": "request",
            "content": {"action": "fetch", "table": "Book"},
            "node": "Node 1",
            "next_nodes": ["ws://localhost:8762", "ws://localhost:8763"]
        }
        await websocket.send(json.dumps(message))

async def forward_message(node_url, message):
    # Function to forward message to other nodes
    async with websockets.connect(node_url) as websocket:
        await websocket.send(json.dumps(message))

async def handle_message(data, websocket, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Execute SQL based on the content of the message
            await cur.execute(f"SELECT * FROM book;")
            result = await cur.fetchall()
            # Send response back to the user or client
            response = {
                "type": "response",
                "content": result,
                "node": "Node 1"
            }
            await websocket.send(json.dumps(response))
            # Concurrently forward a new message to other nodes if specified
            if 'next_nodes' in data:
                tasks = [forward_message(url, {
                    "type": "request",
                    "content": data['content'],
                    "node": data['node']
                }) for url in data['next_nodes']]
                await asyncio.gather(*tasks)

async def receive_message(websocket, path, pool):
    async for message in websocket:
        data = json.loads(message)
        print(data)
        await handle_message(data, websocket, pool)

async def main():
    pool = await start_db_pool()
    server = await websockets.serve(lambda ws, path: receive_message(ws, path, pool), "localhost", 8761)
    await asyncio.gather(server.wait_closed(), send_initial_message())

asyncio.run(main())
