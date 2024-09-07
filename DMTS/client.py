import socket

host = socket.gethostname()  # or use the server's IP address
port = 5000

def client():
    print("transaction <your public address> <destination public address> <your secret> <amount>")
    print("register <new public address> <your secret>")
    print("balance <public address>")
    command = input("$ ")
    tokens = command.split(" ")
    if tokens[0] == "transaction":
        print("sending transaction request...")
        cs = socket.socket()  # instantiate the client socket
        cs.connect((host, port))  # connect to the server
        cs.send("client".encode())
        cs.recv(1)
        cs.send(command.encode())
        print(cs.recv(1024).decode())
        cs.send("exit".encode())
    elif tokens[0] == "register":
        print("sending registration request...")
        cs = socket.socket()  # instantiate the client socket
        cs.connect((host, port))  # connect to the server
        cs.send("client".encode())
        cs.recv(1)
        cs.send(command.encode())
        print(cs.recv(1024).decode())
        cs.send("exit".encode())
    elif tokens[0] == "balance":
        print("sending balance request...")
        cs = socket.socket()  # instantiate the client socket
        cs.connect((host, port))  # connect to the server
        cs.send("client".encode())
        cs.recv(1)
        cs.send(command.encode())
        print(cs.recv(1024).decode())
        cs.send("exit".encode())
    elif tokens[0] == "gdb":
        cs = socket.socket()  # instantiate the client socket
        cs.connect((host, port))  # connect to the server
        cs.send("client".encode())
        cs.recv(1)
        cs.send("get_decentralized_database".encode())
        dbInit = cs.recv(1024).decode()
        if dbInit != "no ddb":
            print(dbInit)
        else:
            print("no ddb")

if __name__ == "__main__":
    client()
