import socket, threading, sys, hashlib
host = socket.gethostname()
port = 5000

server_socket = socket.socket()
server_socket.bind((host, port))

class Action:
    def add(self):
        actions.append(self)

    def completed(self):
        if self in actions:
            actions.remove(self)

class Transaction(Action):
    def __init__(self, conn: socket.socket, sender_p, dest_p, secret, amount):
        self.sender_p = sender_p
        self.dest_p = dest_p
        self.secret = secret
        self.amount = amount
        self.conn = conn
        self.res = False
        self.accepted = 0
        self.denied = 0
        self.deny_reason = ""
        super().add()
        threading.Timer(0.5, self.resolve).start()

    def resolve(self):
        if not self.res:
            if self.accepted == 0 and self.denied == 0:
                self.resolved("failed (took to long)")
                return
            if self.accepted > self.denied:
                self.resolved("accepted")
            else:
                self.resolved(self.deny_reason)

    def resolved(self, state):
        if not self.res:
            self.completed()
            self.conn.send(f"Transaction resolved with state: {state}".encode())
            self.res = True
class Registration(Action):
    def __init__(self, conn: socket.socket, p, secret):
        self.p = p
        self.secret = secret
        self.conn = conn
        self.res = False
        self.successful = 0
        self.denied = 0
        self.deny_reason = ""
        super().add()
        threading.Timer(0.5, self.resolve).start()

    def resolve(self):
        if not self.res:
            if self.successful == 0 and self.denied == 0:
                self.resolved("failed (took to long)")
                return
            if self.successful > self.denied:
                self.resolved("successful")
            else:
                self.resolved(self.deny_reason)

    def resolved(self, state):
        if not self.res:
            self.completed()
            self.conn.send(f"Registration resolved with state: {state}".encode())
            self.res = True
class DDBInitialization(Action):
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.sent = False
        self.versions: dict[str, int] = {}
        super().add()
        threading.Timer(0.5, self.resolve).start()

    def resolve(self):
        if not self.sent:
            if len(self.versions) > 0:
                sorted_versions = sorted(self.versions.items(), key=lambda item: item[1], reverse=True)
                highest_version = sorted_versions[0][0]
                self.conn.send(highest_version.encode())
            else:
                self.conn.send(b"no ddb")
            self.sent = True
            self.completed()
class GetBalance(Action):
    def __init__(self, conn: socket.socket, p):
        self.p = p
        self.conn = conn
        self.sent = False
        self.versions: dict[str, int] = {}
        super().add()
        threading.Timer(0.5, self.resolve).start()

    def resolve(self):
        if not self.sent:
            if len(self.versions) > 0:
                sorted_versions = sorted(self.versions.items(), key=lambda item: item[1], reverse=True)
                highest_version = sorted_versions[0][0]
                self.conn.send(highest_version.encode())
            else:
                self.conn.send(b"no ddb")
            self.sent = True
            self.completed()

actions: list[Action] = []

def client_connection(data: str, conn: socket.socket, addr):
    tokens = data.split(" ")
    if tokens[0] == "transaction":
        Transaction(conn, tokens[1], tokens[2], tokens[3], tokens[4])
    if tokens[0] == "register":
        Registration(conn, tokens[1], hashlib.sha256(tokens[2].encode()).hexdigest())
    if tokens[0] == "get_decentralized_database":
        DDBInitialization(conn)
    if tokens[0] == "balance":
        GetBalance(conn, tokens[1])

def ddb_connection(data: str, conn: socket.socket, addr):
    if data == "get":
        init = DDBInitialization(conn)
        conn.recv(1024)
        while init in actions: continue
    while len(actions) == 0: continue
    if actions and isinstance(actions[0], Transaction):
        action = actions[0]
        transaction: Transaction = action
        conn.send(f"transaction {transaction.sender_p} {transaction.dest_p} {hashlib.sha256(transaction.secret.encode()).hexdigest()} {transaction.amount}".encode())
        data = conn.recv(1024).decode()
        if data == "accepted":
            transaction.accepted += 1
        else:
            transaction.denied += 1
            print("denied! reason:", data)
            transaction.deny_reason = data
        while action in actions: continue
        conn.send("done".encode())
    if actions and isinstance(actions[0], Registration):
        action = actions[0]
        registration: Registration = action
        conn.send(f"register {registration.p} {registration.secret}".encode())
        data = conn.recv(1024).decode()
        if data == "successful":
            registration.successful += 1
        else:
            registration.denied += 1
            print("denied! reason:", data)
            registration.deny_reason = data
        while action in actions: continue
        conn.send("done".encode())
    if actions and isinstance(actions[0], DDBInitialization):
        action = actions[0]
        ddbinit: DDBInitialization = action

        conn.send(b"get")

        ret = conn.recv(1024).decode()
        if ret in ddbinit.versions:
            ddbinit.versions[ret] += 1
        else:
            ddbinit.versions[ret] = 1
        while action in actions: continue
        conn.send("done".encode())
    if actions and isinstance(actions[0], GetBalance):
        action = actions[0]
        gb: GetBalance = action

        conn.send(f"get_bal {gb.p}".encode())

        ret = conn.recv(1024).decode()
        if ret in gb.versions:
            gb.versions[ret] += 1
        else:
            gb.versions[ret] = 1
        while action in actions: continue
        conn.send("done".encode())


def connection(conn: socket.socket, addr):
    try:
        t = conn.recv(1024).decode()
        conn.send("~".encode())
        while True:
            data = conn.recv(1024).decode()
            if not data or data == "exit": break # connection closed

            if t == "client": client_connection(data, conn, addr)
            if t == "ddb": ddb_connection(data, conn, addr)
    except:
        conn.close()
        print("Disconnected abruptly!")

def run():
    while server_socket:
        try:
            server_socket.listen(100)
            conn, address = server_socket.accept()
            threading.Thread(target=connection, args=(conn, address), daemon=True).start()
        except: break

def stop():
    while True:
        if input("") == "exit":
            server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    threading.Thread(target=stop, daemon=True).start()
    run()