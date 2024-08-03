import argparse
import socket
import sys
import threading


class Server:
    def __init__(self, local_host='0.0.0.0', server_port=5000):
        self.local_host = local_host
        self.server_port = server_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_session_quit = False

        # allow reuse of the server address
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # boolean variable to keep track of the server running, this prevents a exception when closing a socket
        self.is_server_running = True

        # vars for hashing functionality
        self.num_hash_req = None

    def initialize(self, conn):
        # Read in number of hash requests
        self.num_hash_req = int(conn.recv(1024).decode('utf-8'))

        # validate
        if self.num_hash_req < 0:
            conn.send('422 UNPROCESSABLE ENTITY: Number of hash requests must be 0 or greater'.encode('utf-8'))

    def acknowledge(self, conn):
        conn.send(f'200 OK:'
                  f'\nType: 2'
                  f'\nTotal length of all hash responses will be {38 * self.num_hash_req}'.encode('utf-8'))

    def connect_client(self, conn, addr):
        print(f'Server connected to client {addr}')

        # this flag variable will keep track if the user has quit or not
        self.is_session_quit = False

        with conn:
            while not self.is_session_quit:
                # initialize and send acknowledgement
                self.initialize(conn)

                if self.num_hash_req >= 0:
                    self.acknowledge(conn)

        print(f'Client {addr} disconnected to server.')

    def start_server(self):
        # create socket connection from local host
        self.tcp_socket.bind((self.local_host, self.server_port))
        self.tcp_socket.listen()

        print(f'Server is started and listening through {self.local_host}:{self.server_port}')

        # establish connection to the client
        while self.is_server_running:
            try:
                conn, adder = self.tcp_socket.accept()

                # use the threading module to keep the server running even if the client quits using callback function
                thread = threading.Thread(target=self.connect_client(conn, adder), args=(conn, adder))
                thread.start()
            except OSError:
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="TCP server to hash segments of a file.")
    parser.add_argument('-p', '--port', help='Port number for the server that is greater than 1024', required=True)

    # Validate all input
    try:
        args = vars(parser.parse_args())

        # validate port number
        if int(args['port']) <= 1024:
            raise Exception("Server.py: error: -p/--port must be greater than 1024")
    except Exception as e:
        print(e)
        sys.exit()

    server = Server(server_port=int(args['port']))
    server.start_server()