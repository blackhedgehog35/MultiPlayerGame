import datetime
import secrets
import random
import socket


LEN_TOTAL_PRINT = 75


def custom_print(word1, word2):
    date = datetime.datetime.now().strftime('|%d/%m/%y %H:%M:%S| ')
    n_space = LEN_TOTAL_PRINT - (len(str(word1)) + len(str(word2)) + len(date))
    print(f"{date}{word1}{'.' * n_space}{word2}")


def generate_key(world) -> str:
    key = secrets.token_hex(3)
    while key in world.keys():
        key = secrets.token_hex(3)
    return key


def generate_pos() -> tuple[int, int]:
    x = random.randint(100, 1000)
    y = random.randint(100, 700)
    return x, y


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
