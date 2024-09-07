import socket
import threading
import sys
import time

host = socket.gethostname()
port = 5000

server_socket = socket.socket()
server_socket.bind((host, port))

class Transaction:
    def __init__(self, h: int, dest: str, amount: int, conn: socket.socket):
        self.h = h
        self.dest = dest
        self.amount = amount
        self.conn = conn
        self.responses = {"confirmed": 0, "denied": 0}
        self.total_ddbs = 3  # Replace with the actual number of DDBs
        self.timer = threading.Timer(1, lambda: self.resolved("Transaction denied! (Took to long?)"))
        self.timer.start()
        print("Added transaction:", h, dest, amount)

    def add_response(self, response: str):
        if response in self.responses:
            self.responses[response] += 1
            if self.responses["confirmed"] > self.total_ddbs // 2:
                self.resolved("Transaction done.")
            elif self.responses["denied"] > self.total_ddbs // 2:
                self.resolved("Transaction denied! (Insufficient funds?)")

    def resolved(self, state: str):
        try:
            self.conn.send(state.encode())
            print(f"Transaction to {self.dest} resolved with state: {state}")
        finally:
            self.conn.close()
            self.remove()


    def remove(self):
        if self in transactions:
            transactions.remove(self)
            update_current_transaction()


class NewClient:
    def __init__(self, h: int, id: str, balance: int):
        self.h = h
        self.id = id
        self.balance = balance
        self.timer = threading.Timer(1, self.remove)
        self.timer.start()

    def remove(self):
        if self in newClients:
            newClients.remove(self)
            update_current_new_client()

transactions: list[Transaction] = []
newClients: list[NewClient] = []
currentTransaction: Transaction = None
currentNewClient: NewClient = None
stop_server = threading.Event()

def update_current_transaction():
    global currentTransaction
    if len(transactions) > 0:
        currentTransaction = transactions[0]
    else:
        currentTransaction = None

def update_current_new_client():
    global currentNewClient
    if len(newClients) > 0:
        currentNewClient = newClients[0]
    else:
        currentNewClient = None

def handle_client(conn: socket.socket, address):
    global currentTransaction, currentNewClient
    try:
        while not stop_server.is_set():
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(data)
                if data.startswith("!client!"):
                    t = data.split(" ")
                    t.pop(0)
                    if t[0] == "transaction":
                        transactions.append(Transaction(hash(t[1]), t[2], int(t[3]), conn))
                        update_current_transaction()
                    if t[0] == "reg":
                        newClients.append(NewClient(hash(t[2]), t[1], 0))
                        update_current_new_client()
                        conn.send("done.".encode())
                elif data == "!ddb! get base":
                    conn.send("no ddb".encode())
                elif data == "!ddb! duty":
                    if currentTransaction:
                        response = f"transaction {currentTransaction.dest} {currentTransaction.amount} {currentTransaction.h}"
                        conn.send(response.encode())
                    elif currentNewClient:
                        response = f"new_client {currentNewClient.h} {currentNewClient.id} 0"
                        conn.send(response.encode())
                    else:
                        conn.send("standby".encode())
                elif data == "!ddb! response confirmed":
                    if currentTransaction:
                        currentTransaction.add_response("confirmed")
                        conn.send("roger".encode())
                elif data == "!ddb! response denied":
                    if currentTransaction:
                        currentTransaction.add_response("denied")
                        conn.send("roger".encode())
                elif data == "!ddb! registration confirmed":
                    print("done registration")
                    conn.send("roger".encode())
                elif data == "!ddb! registration denied":
                    print("failed registration")
                    conn.send("roger".encode())

            except ConnectionAbortedError:
                break
            except ConnectionResetError:
                break

    finally:
        conn.close()


def stopHandler():
    while True:
        if input() != "stop":
            continue
        stop_server.set()
        server_socket.close()
        sys.exit(0)

stop_thread = threading.Thread(target=stopHandler)
stop_thread.start()

while not stop_server.is_set():
    try:
        server_socket.listen(5)
        conn, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, address), daemon=True)
        client_thread.start()
    except OSError:
        break

print("Network stopped.")
