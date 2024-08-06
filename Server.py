import argparse
import socket
import sys
import threading


class Server:
    def __init__(self, local_host='0.0.0.0', server_port=5000):
        self.local_host = local_host
        self.server_port = server_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # allow reuse of the server address
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # vars for hashing functionality
        self.num_hash_req = None


    def initialize(self, conn):
        # Read in number of hash requests
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
                    cur_hash_str = "0x"
                    request = conn.recv(1024).decode('utf-8')

                    if request:
                        print(f'200 OK\nType: 3\nData: {request}\n')

                        for char in request:
                            cur_hash_str += f'{ord(char):02x}'

                        if len(cur_hash_str) < 34:
                            cur_hash_str += ("0" * (34 - len(cur_hash_str)))

                        conn.send(f'200 OK'
                                  f'\nType: 4'
                                  f'\nHash {i}: {cur_hash_str}'.encode('utf-8'))
        except Exception as e:
            print(f'Error: {e}')
        finally:
            print(f'Client {addr} disconnected from server.\n{"-" * 40}')


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
