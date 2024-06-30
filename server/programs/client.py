import pickle
import socket
import server.programs.function


class ClientConn:
    def __init__(self, client_socket: socket.socket, addr, world):
        self.socket = client_socket
        self.address_ip, self.port = addr

        access = True
        #  The client sent his key, we check if he has a key valid or not
        client_response = pickle.loads(client_socket.recv(1024))
        if client_response in world.keys():
            #  User already connected, so we refuse the connection
            if world[client_response]['online']:
                access = False
                server.programs.function.custom_print(f'[CONNECTION] Refused', f'{self.address_ip}:{self.port}')
            else:
                self.KEY = client_response
                self.pos = world[client_response]['pos']
                server.programs.function.custom_print(f'[CONNECTION] With the Key {self.KEY}',
                                                      f'{self.address_ip}:{self.port}')
        else:
            #  No valid key, we generate a new login key
            self.KEY = server.programs.function.generate_key(world)
            self.pos = server.programs.function.generate_pos()
            server.programs.function.custom_print(f'[CREATE] a new key {self.KEY}', f'{self.address_ip}:{self.port}')
        #  We send the final response to the client
        self.socket.sendall(pickle.dumps({'key': self.KEY, 'pos': self.pos} if access else 'no'))

    def send(self, world):
        #  We want to send just user who are connected
        data_to_send = {}
        for key in world.keys():
            #  I add only connected user
            if world[key]['online']:
                data_to_send[key] = world[key]

        self.socket.sendall(pickle.dumps(data_to_send))
