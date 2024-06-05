import miniupnpc
import socket
import pickle
import threading
import server.client
import server.function
from configparser import ConfigParser
"""
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
                """


class Server:
    config = ConfigParser()
    config.read('config.ini')
    world = {}
    PORT = 3055

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', 0))

        self.PORT = self.server_socket.getsockname()[1]
        self.HOST = self.setup_upnp_port_mapping()
        server.function.custom_print("Public IP Address:", self.HOST)
        server.function.custom_print("Public IP Port:", self.PORT)

        self.config.set('server', 'host', self.HOST)
        self.config.set('server', 'port', str(self.PORT))
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def setup_upnp_port_mapping(self):
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        upnp.addportmapping(self.PORT, 'TCP', upnp.lanaddr, self.PORT, 'Python UPnP Port Mapping', '')
        external_ip = upnp.externalipaddress()
        return external_ip

    def client_connection(self, client_socket, addr):
        #  Start of the connection with the client
        client_conn = server.client.ClientConn(client_socket, addr, self.world)
        self.world[client_conn.KEY] = {'online': True, 'pos': client_conn.pos}
        while True:
            try:
                message = pickle.loads(client_socket.recv(1024))
            except EOFError:
                break
            except ConnectionResetError:
                break
            for attribute in message.keys():
                self.world[client_conn.KEY][attribute] = message[attribute]
            client_conn.send(self.world)

        client_conn.socket.close()
        self.world[client_conn.KEY]['online'] = False
        server.function.custom_print('[CONNECTION] End With', f'{client_conn.address_ip}:{client_conn.port}')
        print()

    def start(self):
        self.server_socket.listen()
        print(f"{self.HOST}:{self.PORT}".center(server.function.LEN_TOTAL_PRINT, "="))
        print()
        while True:
            conn, addr = self.server_socket.accept()

            thread = threading.Thread(target=self.client_connection, args=(conn, addr))
            server.function.custom_print('[CONNECTION] Start With', f'{addr[0]}:{addr[1]}')
            thread.start()


