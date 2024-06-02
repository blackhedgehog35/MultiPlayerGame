import pickle
import socket
import threading
from configparser import ConfigParser
from server import get_public_ip, get_local_ip, custom_print, len_total_print, world, check_key_format, generate_key, generate_pos


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
        address, port = addr
        custom_print('[CONNECTION] Start With', address)
        client_response = pickle.loads(client_socket.recv(1024))
        #  The client sent his key, we check if he has a key valid or not (just the syntax)
        if check_key_format(client_response):
            if client_response in world.keys():
                if world[client_response]['online']:
                    server_response = 'no'
                    custom_print('[CONNECTION] Refused With', address)
                else:
                    key = client_response
                    pos = world[key]['pos']
                    server_response = {'key': key, 'start pos': pos}
            else:
                key = generate_key()
                pos = generate_pos()
                server_response = {'key': key, 'start pos': pos}
        else:
            key = generate_key()
            pos = generate_pos()
            server_response = {'key': key, 'start pos': pos}
            custom_print(f'[CREATE] a new key {key}', address)
        """
        if not check_key_format(key):
            new_key = generate_key()
            custom_print(f'[CHANGE KEY] {key if key else "None"} => {new_key}', address)
            key = new_key
            pos = generate_pos()
            server_response = {'key': key, 'pos': pos}
        elif key in world.keys():
            server_response = 'no'
            custom_print('[CONNECTION] Refused With', address)
        else:
            print('[LOGGED] With Key:')
            server_response = {'key': key, 'pos': }
        """
        client_socket.sendall(pickle.dumps(server_response))
        world[key] = {'online': True}
        while True:
            try:
                message = pickle.loads(client_socket.recv(1024))
            except EOFError:
                break
            except ConnectionResetError:
                break
            for attribute in message.keys():
                world[key][attribute] = message[attribute]
            print(f'\r{world}', end="")
            client_socket.sendall(pickle.dumps(world))

        client_socket.close()
        world[key]['online'] = False
        custom_print('[CONNECTION] End With', address)
        print(world)

    def start(self):
        self.server_socket.listen()
        print(f"{self.HOST}:{self.PORT}".center(len_total_print, "="))
        while True:
            conn, addr = self.server_socket.accept()
            thread = threading.Thread(target=self.client_connection, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    NewServer().start()
