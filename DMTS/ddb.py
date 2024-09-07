import socket, hashlib
import time
from tempfile import gettempdir

host = socket.gethostname()  # or use the server's IP address
port = 5000

db: dict[str, [str, int]] = {
    "admin": [hashlib.sha256(b"admin123.").hexdigest(), 1000]
}

def ddb():
    global db
    cs = socket.socket()  # instantiate the client socket
    cs.connect((host, port))  # connect to the server

    cs.send("ddb".encode())
    cs.recv(1)
    cs.send("get".encode())
    dbInit = cs.recv(1024).decode()
    if dbInit != "no ddb":
        print(dbInit)
        db = eval(dbInit)
    else:
        print("no ddb")
    while True:
        cs.send("ready".encode())
        command = cs.recv(1024).decode()
        tokens = command.split(" ")
        if tokens[0] == "transaction":
            print("transaction", command)
            if tokens[1] in db and tokens[2] in db:
                if db[tokens[1]][0] == tokens[3]:
                    if db[tokens[1]][1] >= int(tokens[4]):
                        if int(tokens[4]) > 0:
                            cs.send("accepted".encode())
                            db[tokens[1]][1] -= int(tokens[4])
                            db[tokens[2]][1] += int(tokens[4])
                            print("accepted")
                        else:
                            cs.send("transaction amount cannot be smaller than zero nor be zero!".encode())
                    else:
                        cs.send("insufficient funds to complete transaction!".encode())
                else:
                    cs.send("wrong secret!".encode())
            else:
                cs.send("sender or receiver is not registered!".encode())
            cs.recv(1024)
        if tokens[0] == "register":
            print("registration", command)
            if not tokens[1] in db:
                db[tokens[1]] = [tokens[2], 0]
                cs.send(b"successful")
                print("successful")
            else:
                cs.send("pubic address taken!".encode())
            cs.recv(1024)
        if tokens[0] == "get":
            print("sending db")
            cs.send(str(db).encode())
        if tokens[0] == "get_bal":
            print("getting balance of user:", tokens[1])
            if tokens[1] in db:
                cs.send(str(db[tokens[1]][1]).encode())
            else:
                cs.send(b"nonexistent id!")
            cs.recv(1024)

if __name__ == "__main__":
    ddb()
