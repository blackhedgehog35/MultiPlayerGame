import pickle
import socket
import threading
from configparser import ConfigParser
from server import (get_public_ip, get_local_ip, custom_print, LEN_TOTAL_PRINT, world, check_key_format, generate_key,
                    generate_pos, ClientConn)


class NewServer:
    config = ConfigParser()
    config.read('config.ini')
    PORT = 3010

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.public_ip = get_public_ip()
        if self.public_ip:
            custom_print("Public IP Address:", self.public_ip)
        else:
            custom_print("[ERROR]", "Cannot take public address")
        self.local_ip = get_local_ip()
        if self.local_ip:
            custom_print("Local IP Address:", self.local_ip)
        else:
            custom_print("[ERROR]", "Cannot take local address")
        try:
            self.server_socket.bind((self.public_ip, self.PORT))
            self.HOST = self.public_ip
        except OSError:
            try:
                self.server_socket.bind((self.local_ip, self.PORT))
                self.HOST = self.local_ip
            except OSError:
                self.server_socket.bind(('127.0.0.1', self.PORT))
                self.HOST = '127.0.0.1'

        self.config.set('server', 'host', self.HOST)
        self.config.set('server', 'port', str(self.PORT))
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    @staticmethod
    def client_connection(client_socket, addr):
        #  Start of the connection with the client
        client = ClientConn(client_socket, addr)
        world[client.KEY] = {'online': True, 'pos': client.pos}
        while True:
            try:
                message = pickle.loads(client_socket.recv(1024))
            except EOFError:
                break
            except ConnectionResetError:
                break
            for attribute in message.keys():
                world[client.KEY][attribute] = message[attribute]
            client.send()

        client.socket.close()
        world[client.KEY]['online'] = False
        custom_print('[CONNECTION] End With', f'{client.address_ip}:{client.port}')
        custom_print('[WORLD]: ', world)

    def start(self):
        self.server_socket.listen()
        print(f"{self.HOST}:{self.PORT}".center(LEN_TOTAL_PRINT, "="))
        while True:
            conn, addr = self.server_socket.accept()

            thread = threading.Thread(target=self.client_connection, args=(conn, addr))
            custom_print('[CONNECTION] Start With', f'{addr[0]}:{addr[1]}')
            thread.start()


if __name__ == "__main__":
    NewServer().start()
