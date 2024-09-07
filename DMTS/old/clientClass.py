import socket

class Client:
    def __init__(self, h, id, bal):
        self.h = h
        self.id = id
        self.bal = bal
        self.conn = None