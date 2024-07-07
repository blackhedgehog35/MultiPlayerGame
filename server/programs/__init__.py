import sys
import socket
import pickle
import miniupnpc
import threading
import server.programs.client
import server.programs.function


class Server:
    world = {}
    PORT = 3055

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', 0))

        self.PORT = self.server_socket.getsockname()[1]
        try:
            self.HOST = self.setup_upnp_port_mapping()
        except Exception:
            server.programs.function.custom_print('[ERROR]', 'cannot open connection.')
            sys.exit()

        server.programs.function.custom_print("Public IP Address:", self.HOST)
        server.programs.function.custom_print("Public IP Port:", self.PORT)
        self.threads = []
        self.stop_event = threading.Event()

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
        client_conn = server.programs.client.ClientConn(client_socket, addr, self.world)
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
        server.programs.function.custom_print('[CONNECTION] End With', f'{client_conn.address_ip}:{client_conn.port}')

    def input_server(self):
        while True:
            message = input('')
            if message.lower() in ['world', 'echo', 'print']:
                print(self.world)
            elif message.lower() in ['test']:
                self.stop_server()

    def start(self):
        self.server_socket.listen()
        print(f"{self.HOST}:{self.PORT}".center(server.programs.function.LEN_TOTAL_PRINT, "="))
        thread = threading.Thread(target=self.input_server)
        thread.start()
        while True:
            conn, addr = self.server_socket.accept()

            thread = threading.Thread(target=self.client_connection, args=(conn, addr))
            print()
            server.programs.function.custom_print('[CONNECTION] Start With', f'{addr[0]}:{addr[1]}')
            thread.start()
            self.threads.append(thread)

    def stop_server(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join()
        print("All client connections closed")
