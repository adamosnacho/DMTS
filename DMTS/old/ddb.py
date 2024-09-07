import socket
import clientClass
import time

host = socket.gethostname()
port = 5000

db: clientClass.Client = []

ddb_socket = socket.socket()
ddb_socket.connect((host, port))
ddb_socket.send("!ddb! get base".encode())
data = ddb_socket.recv(1024).decode()
ddb_socket.close()

if data == "no ddb":
    print("no other ddb on network, blank db")
else:
    db = eval(data)


# Function to handle periodic duty checks
def perform_duty_check():
    global db
    state = "duty"
    while True:
        ddb_socket = socket.socket()
        ddb_socket.connect((host, port))
        if state == "duty": ddb_socket.send("!ddb! duty".encode())
        if state == "response confirmed":
            ddb_socket.send("!ddb! response confirmed".encode())
            state = "duty"
        if state == "response denied":
            ddb_socket.send("!ddb! response denied".encode())
            state = "duty"
        if state == "registration denied":
            ddb_socket.send("!ddb! registration denied".encode())
            state = "duty"
        if state == "registration confirmed":
            ddb_socket.send("!ddb! registration confirmed".encode())
            state = "duty"

        data = ddb_socket.recv(1024).decode()
        ddb_socket.close()

        if data == "standby":
            print(data)
        elif data == "roger":
            print("rogered")
        else:
            t = data.split(" ")
            if t[0] == "transaction":
                print(data)
                brk = False
                for c in db:
                    c: clientClass.Client
                    if c.h == t[3]:
                        if (c.bal >= int(t[2])): state = "response confirmed"
                        else: state = "response denied"
                        brk = True
                        break
                
                if not brk: state = "response denied"
            if t[0] == "new_client":
                print("new client")
                brk = False
                for c in db:
                    if c.id == t[2]:
                        brk = True
                        state = "registration denied"
                        break

                if not brk:
                    db.append(clientClass.Client(t[1], t[2], 0))
                    state = "registration confirmed"
        time.sleep(0.25)


# Continuously perform duty checks
perform_duty_check()
