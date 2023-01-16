import socket
import time
import json
import logging


logging.basicConfig(level = logging.INFO)

class WebClient():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger = logging.getLogger('tcpclient')
    connected = False
    def __init__(self) -> None:
        self.client_socket.settimeout(10)
        pass

    def connect_to_server(self, nickname) -> bool:
        server = ("127.0.0.1",8888)
        for _ in range(5):
            try:
                if not self.connected:
                    self.client_socket.connect(server)
                    self.connected = True
                    message = {
                        'operation': 'SET_NAME',
                        'username': nickname
                    }

                    self.client_socket.sendall((json.dumps(message) + "\n").encode('utf-8'))
                    
                    reply = self.client_socket.recv(4096)
                    data = json.loads(reply.decode("utf-8"))
                    print(data)
                    if data['response'] == 1:
                        self.logger.info("Username has been accepted")
                        return True
                    else:
                        self.logger.info("Username has not been accepted")
                        return False
                else:
                    message = {
                        'operation': 'SET_NAME',
                        'username': nickname
                    }

                    self.client_socket.sendall((json.dumps(message) + "\n").encode('utf-8'))
                    
                    reply = self.client_socket.recv(4096)
                    data = json.loads(reply.decode("utf-8"))
                    print(data)
                    if data['response'] == 1:
                        self.logger.info("Username has been accepted")
                        return True
                    else:
                        self.logger.info("Username has not been accepted")
                        return False
            except Exception:
                print("TIMEOUT")
                time.sleep(1)
                continue
        return False


    def get_lobby_status(self) -> bool:
        try:
            reply = self.client_socket.recv(4096)
            data = json.loads(reply.decode("utf-8"))
            print(data)
            if data['message'] == "10_SECOND_ALERT":
                self.logger.info("10 second alert")
                return True
            else:
                self.logger.info(data['message'])
                return False
        except TimeoutError:
            print("TIMEOUT")


    def close_socket(self):
        self.client_socket.close()
        print("CLOSED SOCKET")