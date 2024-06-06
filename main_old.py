# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


#def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    #print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
    #print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

import time
import threading
from transaction_chops import TransactionChopper

# tables and corresponding servers
server_tables = {
    1: ['book', 'member'],
    2: ['book', 'member'],
    3: ['borrow', 'reservation'],
    4: ['fine', 'staff']
}

# server data
servers = {
    1: {'book': [], 'member': []},
    2: {'book': [], 'member': []},
    3: {'borrow': [], 'reservation': []},
    4: {'fine': [], 'staff': []},
}

locks = {i: threading.Lock() for i in servers.keys()}

# Timestamp for ordering transactions
current_timestamp = 0
timestamp_lock = threading.Lock()

def get_timestamp():
    global current_timestamp
    with timestamp_lock:
        current_timestamp += 1
        return current_timestamp

# Simulating transaction hop on a server
def execute_transaction(server_id, operation, data):
    # Extract the table name from the operation string
    if " from " in operation:
        table = operation.split(" from ")[1].split()[0]
    elif " into " in operation:
        table = operation.split(" into ")[1].split()[0]
    elif "update " in operation:
        table = operation.split("update ")[1].split()[0]
    else:
        table = None
    
    if table is None or table not in servers[server_id]:
        raise KeyError(f"Table '{table}' not found on server {server_id}")
    
    with locks[server_id]:
        timestamp = get_timestamp()
        servers[server_id][table].append((operation, data, timestamp))
        print(f"Server {server_id}: Executes {operation} with data {data} at timestamp {timestamp}")

# Executing a specific transaction hop
def execute_transaction_hop(transaction_id, operation, server_id, params):
    sql_statement = f"{operation} VALUES ({', '.join(str(param) for param in params)})"
    data = {'transaction_id': transaction_id, 'operation': operation, 'params': params}
    execute_transaction(server_id, sql_statement, data)

# Process the transaction
def process_transaction(transaction_id, operations):
    for operation, server_id, params in operations:
        execute_transaction_hop(transaction_id, operation, server_id, params)
        time.sleep(0.1)

def main():
    chopper = TransactionChopper()
    transactions = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']

    threads = []
    for transaction_id in transactions:
        operations = chopper.get_chops(transaction_id)
        #print(operations)
        thread = threading.Thread(target=process_transaction, args=(transaction_id, operations))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
