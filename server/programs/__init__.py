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
        self.HOST = self.setup_upnp_port_mapping()

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
        try:
            client_conn = server.programs.client.ClientConn(client_socket, addr, self.world)
        except AttributeError:
            pass
        else:
            while True:
                try:
                    message = pickle.loads(client_socket.recv(1024))
                except EOFError:
                    break
                except ConnectionResetError:
                    break
                else:
                    for attribute in message.keys():
                        self.world[client_conn.KEY][attribute] = message[attribute]
                    client_conn.send(self.world)
            self.world[client_conn.KEY] = {'online': True, 'pos': client_conn.pos}
            client_conn.socket.close()
            self.world[client_conn.KEY]['online'] = False
        finally:
            server.programs.function.custom_print('[CONNECTION] End With',
                                                  f'{addr[0]}:{addr[1]}')

    def input_server(self):
        while True:
            message = input('')
            if message.lower() in ['world', 'echo', 'print']:
                print(self.world)
            elif message.lower() in ['reset']:
                new_world = {}
                for key in self.world.keys():
                    if self.world[key]['online']:
                        new_world[key] = self.world[key]
                print(f'{self.world} ==> {new_world}')
                self.world = new_world
            else:
                print("Don't understand the command.")

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
