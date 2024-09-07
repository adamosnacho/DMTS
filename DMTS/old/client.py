import socket

host = socket.gethostname()  # as both code is running on the same PC
port = 5000  # socket server port number

client_socket = socket.socket()  # instantiate
client_socket.connect((host, port))  # connect to the server

message = input("$ ")
client_socket.send(("!client! " + message).encode())
data = client_socket.recv(1024).decode()

print('Status: ' + data)

