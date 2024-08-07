import pickle
import socket


class UserAlreadyConnected(Exception):
    """This custom exception appears when a player is already connected with the key, this allows two users not to play
    the same player at the same time"""

    def __init__(self, key):
        self.client_key = key
        super().__init__(self.client_key)

    def __str__(self):
        return (f"An user is already connected and is playing with the [{self.client_key}] key, "
                "please, create a new key...")


class ServerNoFound(Exception):
    """This custom exception appears when the connection between the client and the server could not be made"""

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        super().__init__((self.HOST, self.PORT))

    def __str__(self):
        return f"The server does not respond, please, make you sure that the host address is {self.HOST}:{self.PORT}"


class ServerClosed(Exception):
    """This custom exception appears when the connection between the client and the server are stopped"""

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        super().__init__((self.HOST, self.PORT))

    def __str__(self):
        return f"Connection closed, the server {self.HOST}:{self.PORT} is shutdown"


class ClientNetwork:
    #  A variable to know if the connection is done between the server and the client
    connected = False

    """
    It is this class which will manage the connections between the server and the client, client part.
    This class must be initialized in the init, after the connection is made, a key will be stored in the KEY variable.
    """
    def __init__(self, host, port, key=""):
        self.HOST = host
        self.PORT = port
        #  The key allows customers to connect with a character, this is how it stores positions
        self.KEY = key
        self.spawn_pos = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        self.connected = True

    def connect(self):
        try:
            self.client_socket.connect((self.HOST, self.PORT))
            #  The client sends its key, if it is empty or invalid, the server sends back a new valid key
            self.client_socket.sendall(pickle.dumps(self.KEY))
            server_respond = pickle.loads(self.client_socket.recv(1024))
            if server_respond == 'no':
                #  When the server returns "no", it means a user is already logged in
                raise UserAlreadyConnected(self.KEY)
            else:
                self.KEY = server_respond['key']
                self.spawn_pos = server_respond['pos']
            self.connected = True

        #  Exception when an error with the server appears, for example if the server is not started
        except EOFError:
            raise ServerNoFound(self.HOST, self.PORT)
        except OSError:
            raise ServerNoFound(self.HOST, self.PORT)
        else:
            self.connected = True

    #  This is the function to send information
    def send(self, data):
        try:
            #  First we send "data" to the server,
            self.client_socket.sendall(pickle.dumps(data))
            #  Then the server sends us back a response.
            return pickle.loads(self.client_socket.recv(1024))
            #  I use pickle to be able to send variables, dictionaries and much more.

        except EOFError:
            return "Connection closed, the server is shutdown"

    def send_attribute(self, pos):
        #  This function will be the main function in the pygame loop to send information. We send the main attributes
        #  to the server, and it returns all the characters on the map as well as their position
        try:
            pos = round(pos[0], 1), round(pos[1], 1)
            #  We send dictionaries
            self.client_socket.sendall(pickle.dumps({'pos': pos}))
            return pickle.loads(self.client_socket.recv(1024))
        except EOFError:
            raise ServerClosed(self.HOST, self.PORT)
        except BrokenPipeError:
            raise ServerClosed(self.HOST, self.PORT)

    def close_connection(self):
        pass
