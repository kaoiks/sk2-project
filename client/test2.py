import socket
import time
import json

server = ("127.0.0.1", 8888)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server)
print("CONNECTED")
message = {
    'nickname': 'MIETEK',
    'es': 21,
    'users': [{'nickname': 'MIETEK'},{'nickname': 'MIETEK'}, {'nickname': 'MIETEK'}, {'nickname': 'MIETEK'}, {'nickname': 'MIETEK'}]
}

client_socket.sendall((json.dumps(message) + "\n").encode('utf-8'))
time.sleep(100000)
client_socket.close()