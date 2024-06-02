import random
import socket
import secrets
import requests

world = {'ae4b3c': {'pos': (255, 258), 'online': False, 'stat': 'Walk'}}
len_total_print = 46


class ServerNetwork:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.start()

    def start(self):
        self.server_socket.listen()

    def accept(self):
        return self.server_socket.accept()


def custom_print(word1, word2):
    n_space = len_total_print - (len(str(word1)) + len(str(word2)))
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


def generate_key():
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

