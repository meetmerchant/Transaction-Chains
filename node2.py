import asyncio
import websockets
import json
import aiomysql

server_ports = {
    1: 8761,
    2: 8762,
    3: 8763,
    4: 8764
}


async def send_message_to_server(port, message):
    uri = f"ws://localhost:{port}"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            print(f"Response from server: {response}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection to server on port {port} closed unexpectedly: {e}")
    except Exception as e:
        print(f"An error occurred while communicating with the server on port {port}: {e}")



async def start_db_pool():
    return await aiomysql.create_pool(
        host='localhost', port=3306,
        user='root', password='Meet@123',
        db='library2', charset='utf8',
        autocommit=True)


async def send_initial_message():
    # Simulating an initial message sent to Node 1 from a client
    await asyncio.sleep(2)
    async with websockets.connect('ws://localhost:8762') as websocket:
        message = {
            "node": "System Check",
            "transaction_id": "initial_check",
            "chops": [],  # No operations to be performed
            "timestamp": 0,
            "message": "System initial check - no operations",
            "next_nodes": []
        }
        await websocket.send(json.dumps(message))


async def forward_message(node_url, message):
    # Function to forward message to other nodes
    async with websockets.connect(node_url) as websocket:
        await websocket.send(json.dumps(message))


async def handle_message(transaction_id, chops, timestamp, websocket, pool):
    print("Inside handler")
    if not chops:
        print("No chops available to process.")
        return

        # Process the first chop
    first_chop = chops[0]
    query, node_id, params = first_chop

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            result = await cur.fetchall()
            response = {
                "type": "response",
                "content": result,
                "node": f"Node {node_id}"
            }
            # await websocket.send(json.dumps(response))

    print(f"Executed transaction {transaction_id} with query {query} at timestamp {timestamp}")

    # Remove the first chop which has been processed
    remaining_chops = chops[1:]

    # If there are remaining chops, determine the node for the next chop and send only to that node
    if remaining_chops:
        next_chop = remaining_chops[0]
        next_node_id = next_chop[1]
        next_server_port = server_ports.get(next_node_id)

        print(f"Continuing transaction {transaction_id} with timestamp {timestamp} at next node {node_id}")

        message = {
            "node": f"Node {node_id}",
            "transaction_id": transaction_id,
            "chops": remaining_chops,
            "timestamp": timestamp,
            "message": f"Continuing transaction {transaction_id} at timestamp {timestamp}"
        }
        await send_message_to_server(next_server_port, message)


async def receive_message(websocket, path, pool):
    # Define batch time in seconds
    batch_time = 10  # Adjust this value as needed

    while True:
        received_data = []
        start_time = asyncio.get_event_loop().time()

        try:
            # Collect messages for a batch time duration
            while True:
                # Break the loop if the batch time has exceeded
                if (asyncio.get_event_loop().time() - start_time) > batch_time:
                    break
                try:
                    # Try to receive a message within the remaining batch time
                    remaining_time = batch_time - (asyncio.get_event_loop().time() - start_time)
                    message = await asyncio.wait_for(websocket.recv(), timeout=remaining_time)
                    data = json.loads(message)
                    received_data.append(data)
                    print("Received message: ", data)
                except asyncio.TimeoutError:
                    # No message received within the remaining batch time
                    break

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            continue  # Skip this message and continue with the next
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed unexpectedly: {e}")
            break

        if received_data:
            # print("Received data before sorting: ", received_data)
            # Sort the received data based on the 'timestamp' key
            received_data.sort(key=lambda x: x['timestamp'])
            # print("Received data after sorting: ", received_data)

            # Process each message in order of their timestamps
            for data in received_data:
                transaction_id = data.get("transaction_id")
                chops = data.get("chops")
                timestamp = data.get("timestamp")
                await handle_message(transaction_id, chops, timestamp, websocket, pool)



async def main():
    pool = await start_db_pool()
    server = await websockets.serve(lambda ws, path: receive_message(ws, path, pool), "localhost", 8762)
    await asyncio.gather(server.wait_closed(), send_initial_message())


asyncio.run(main())
