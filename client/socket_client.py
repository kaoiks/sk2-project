import socket

HOST = "127.0.0.1"
PORT = 8080
class ClientSocket(socket.socket):
    
    def __init__(self, family=socket.AF_INET, sock_type = socket.SOCK_STREAM) -> None:
        super().__init__(family, sock_type)

    def connect_to_server(self):
        self.connect((HOST, PORT))

    def read_data(self):
        data = self.recv(1024)
        print(data)

    def send_data(self):
        self.send("Hello, world".encode())

