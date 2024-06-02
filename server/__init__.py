import random
import socket
import pickle
import secrets
import requests
#  world = {'test': {'pos': (x, y), 'online': bool, 'stat': 'Walk'}}
world = {}
LEN_TOTAL_PRINT = 52


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

        self.socket.sendall(pickle.dumps({'key': self.KEY, 'pos': self.pos} if access else 'no'))

    def send(self):
        #  We want to send just user who are connected
        data_to_send = {}
        for key in world.keys():
            if world[key]['online']:
                data_to_send[key] = world[key]

        self.socket.sendall(pickle.dumps(data_to_send))


def custom_print(word1, word2):
    n_space = LEN_TOTAL_PRINT - (len(str(word1)) + len(str(word2)))
    print(f"{word1}{'.' * n_space}{word2}")


def is_hexadecimal(chaine):
    if not chaine or chaine == "":
        return False

    hex_chars = set('0123456789abcdefABCDEF')
    for char in chaine:
        if char not in hex_chars:
            return False

    return True


def check_key_format(key):
    if len(key) != 6 or not is_hexadecimal(key):
        return False
    return True


def generate_key() -> str:
    key = secrets.token_hex(3)
    while key in world.keys():
        key = secrets.token_hex(3)
    return key


def generate_pos():
    x = random.randint(20, 600)
    y = random.randint(20, 400)
    return (x, y)


def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException:
        return None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(e)
        return None

