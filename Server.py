import argparse
import json
import socket
import sys
import threading
import random


class Server:
    def __init__(self, local_host='0.0.0.0', server_port=5000):
        self.local_host = local_host
        self.server_port = server_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # handle multiple clients
        self.lock = threading.Lock()

        # allow reuse of the server address
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # vars for hashing functionality
        self.num_hash_req = None
        self.num_L_bytes = None


    def initialize(self, conn):
        # Read in number of hash requests, smin, smax as one object
        self.num_hash_req = int(conn.recv(1024).decode('utf-8'))

        # show initialization response to server terminal
        print(f'200 OK\nType: 1\nInitialization Complete\n')


    def acknowledge(self, conn):
        conn.send(f'200 OK'
                  f'\nType: 2'
                  f'\nTotal length of all hash responses will be {38 * self.num_hash_req}\n'.encode('utf-8'))


    def connect_client(self, conn, addr):
        print(f'Server connected to client {addr}')

        try:
            with conn:
                # initialize and send acknowledgement to client
                self.initialize(conn)

                if self.num_hash_req >= 0:
                    self.acknowledge(conn)

                # begin reading in hash requests
                for i in range(self.num_hash_req):
                    # build a new hash string from scratch for each iteration
                    cur_hash_str = "0x"

                    # request contains the line of text itself and L
                    request = json.loads(conn.recv(1024).decode('utf-8'))
                    line = request['line']
                    num_L_bytes = request['num_L_bytes']

                    if line and len(line) <= 16:
                        print(f'200 OK\nType: 3\nData: {line}\n')

                        for char in line:
                            cur_hash_str += f'{ord(char):02x}'

                        if len(cur_hash_str) < 34:
                            cur_hash_str += ("0" * (34 - len(cur_hash_str)))

                        conn.send(f'200 OK'
                                  f'\nType: 4'
                                  f'\nHash {i}: {cur_hash_str}'
                                  f'\nL Bytes Read: {num_L_bytes}'.encode('utf-8'))

                    if len(line) > 16:
                        conn.send(f'Error: Line {i + 1} has more than 16 chars.'.encode('utf-8'))
                        raise Exception(f'Error: File line {i + 1} has more than 16 chars.')

        except Exception as e:
            print(f'Error: {e}')
        finally:
            print(f'Client {addr} disconnected from server.\n')


    def start_server(self):
        # create socket connection from local host
        self.tcp_socket.bind((self.local_host, self.server_port))
        self.tcp_socket.listen()

        print(f'Server is started and listening through {self.local_host}:{self.server_port}')

        # establish connection to the client
        while True:
            try:
                conn, adder = self.tcp_socket.accept()

                # use the threading module to keep the server running even if the client quits using callback function
                thread = threading.Thread(target=self.connect_client, args=(conn, adder))
                thread.start()
            except OSError as e:
                print(e)
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="TCP server to hash segments of a file.")
    parser.add_argument('-p', '--port', help='Port number for the server that is greater than 1024', required=True)

    # Validate all input
    try:
        args = vars(parser.parse_args())

        # validate port number
        if int(args['port']) <= 1024:
            raise Exception("Server.py: error: -p / --port must be greater than 1024")

        server = Server(server_port=int(args['port']))
        server.start_server()
    except Exception as e:
        print(e)
        sys.exit()
