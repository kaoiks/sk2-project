import socket
import time


server = ("127.0.0.1",8080)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server)
data = client_socket.recv(1024)
print(data)
client_socket.close()