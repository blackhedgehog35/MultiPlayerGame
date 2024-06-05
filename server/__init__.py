import pytz
import random
import socket
import pickle
import secrets
import requests
import threading
from datetime import datetime
from configparser import ConfigParser

#  world = {'test': {'pos': (x, y), 'online': bool, 'stat': 'Walk'}}
paris_tz = pytz.timezone('Europe/Paris')
world = {}
LEN_TOTAL_PRINT = 75


class Server:
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
        print()

    def start(self):
        self.server_socket.listen()
        print(f"{self.HOST}:{self.PORT}".center(LEN_TOTAL_PRINT, "="))
        print()
        while True:
            conn, addr = self.server_socket.accept()

            thread = threading.Thread(target=self.client_connection, args=(conn, addr))
            custom_print('[CONNECTION] Start With', f'{addr[0]}:{addr[1]}')
            thread.start()


class ClientConn:
    def __init__(self, client_socket: socket.socket, addr):
        self.socket = client_socket
        self.address_ip, self.port = addr

        access = True
        #  The client sent his key, we check if he has a key valid or not
        client_response = pickle.loads(client_socket.recv(1024))
        if client_response in world.keys():
            #  User already connected, so we refuse the connection
            if world[client_response]['online']:
                access = False
                custom_print(f'[CONNECTION] Refused', f'{self.address_ip}:{self.port}')
            else:
                self.KEY = client_response
                self.pos = world[client_response]['pos']
                custom_print(f'[CONNECTION] With the Key {self.KEY}', f'{self.address_ip}:{self.port}')
        else:
            #  No valid key, we generate a new login key
            self.KEY = generate_key()
            self.pos = generate_pos()
            custom_print(f'[CREATE] a new key {self.KEY}', f'{self.address_ip}:{self.port}')
        #  We send the final response to the client
        self.socket.sendall(pickle.dumps({'key': self.KEY, 'pos': self.pos} if access else 'no'))

    def send(self):
        #  We want to send just user who are connected
        data_to_send = {}
        for key in world.keys():
            #  I add only connected user
            if world[key]['online']:
                data_to_send[key] = world[key]

        self.socket.sendall(pickle.dumps(data_to_send))


def custom_print(word1, word2):
    date = datetime.now(paris_tz).strftime('|%d/%m/%y %H:%M:%S| ')
    n_space = LEN_TOTAL_PRINT - (len(str(word1)) + len(str(word2)) + len(date))
    print(f"{date}{word1}{'.' * n_space}{word2}")


def generate_key() -> str:
    key = secrets.token_hex(3)
    while key in world.keys():
        key = secrets.token_hex(3)
    return key


def generate_pos() -> tuple[int, int]:
    x = random.randint(100, 1100)
    y = random.randint(100, 700)
    return x, y


def get_public_ip() -> str:
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return None


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(e)
        return None
