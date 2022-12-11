import socket
import time

class WebClient():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self) -> None:
        pass

    def connect_to_server(self) -> bool:
        server = ("127.0.0.1",8888)
        for _ in range(5):
            try:
                self.client_socket.connect(server)
                return True
            except Exception:
                time.sleep(1)
                continue
        return False

    def close_socket(self):
        self.client_socket.close()
        print("CLOSED SOCKET")