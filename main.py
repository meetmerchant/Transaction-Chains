import asyncio
import websockets
import json

from transaction_chops import TransactionChopper

# Initialize TransactionChopper
chopper = TransactionChopper()

# Mapping of server IDs to WebSocket ports
server_ports = {
    1: 8761,
    2: 8762,
    3: 8763,
    4: 8764
}

# Function to send a message to the target server
async def send_message_to_server(port, message):
    uri = f"ws://localhost:{port}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"Response from server: {response}")

async def process_transaction(transaction_id):
    chops = chopper.get_chops(transaction_id)

    if not chops:
        print(f"No chops found for transaction ID: {transaction_id}")
        return

    # Get the server ID of the first hop
    first_hop = chops[0]
    server_id = first_hop[1]

    # Get the port of the target server
    server_port = server_ports.get(server_id)

    if server_port is None:
        print(f"Invalid server ID: {server_id}")
        return

    message = {
        "node": "main.py",
        "message": f"Executing transaction {transaction_id}",
        "chops": chops
    }

    await send_message_to_server(server_port, message)


async def main():
    transactions = chopper.chops.keys()

    tasks = [process_transaction(transaction_id) for transaction_id in transactions]

    await asyncio.gather(*tasks)

asyncio.run(main())

