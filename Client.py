import argparse
import socket
import sys
import threading


class Client:
    def __init__(self, file, num_requests, s_min, s_max, address='127.0.0.1', server_port=5000):
        self.file = file
        self.num_requests = num_requests
        self.s_min = s_min
        self.s_max = s_max
        self.local_host = address
        self.server_port = server_port

        # self.lock keeps file reading in sync
        self.lock = threading.Lock()


    def send_line(self, tcp_socket, line):
        with self.lock:
            tcp_socket.send(line.encode('utf-8'))
            response = tcp_socket.recv(1024).decode('utf-8')
            print(response + '\n')


    def start_program(self, tcp_socket):
        tcp_socket.send(str(self.num_requests).encode('utf-8'))

        # acknowledgement response
        response = tcp_socket.recv(1024).decode('utf-8')
        print(response)

        # begin sending hash requests line by line in specified text file using threads
        threads = []

        try:
            with open(self.file, "r") as f:
                # validate number of requests by comparing num lines with num requests
                num_lines = len(f.readlines())

                if num_lines != self.num_requests:
                    raise Exception('Error: Number of requests does not match number of lines in file.')

                # reset file reader
                f.seek(0)

                for line in f:
                    # clean up each line in the text file
                    line = line.strip()
                    if not line:
                        continue

                    # Create a thread for each line to send concurrently
                    thread = threading.Thread(target=self.send_line, args=(tcp_socket, line))
                    thread.start()
                    threads.append(thread)

            # Wait for all threads to finish
            for thread in threads:
                thread.join()

            f.close()

        except Exception as e:
            print(e)



    def start_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            try:
                # Connect to the server
                tcp_socket.connect((self.local_host, self.server_port))
                self.start_program(tcp_socket)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client to send hash requests from a file.")
    parser.add_argument('-a', '--address', help='IP address of the machine the server is running on', required=True)
    parser.add_argument('-p', '--port', help='Port number for the client', type=int, required=True)
    parser.add_argument('-n', '--num-requests', help='N number of hash requests sent to the server that '
                                                     'is >= 0', type=int, required=True)
    parser.add_argument('-smin', '--size-minimum', help='Minimum size for the data payload >= 1', type=int, required=True)
    parser.add_argument('-smax', '--size-maximum', help='Maximum size for the data payload <= 224>', type=int, required=True)
    parser.add_argument('-f', '--file', help='File name that will be read for all hash requests. File must have '
                                             'enough data to support n requests', required=True)

    try:
        args = vars(parser.parse_args())

        # validate all args
        if args['num_requests'] < 0:
            raise Exception("Client.py: error: -n / --num-requests Must be greater than or equal to 0")

        if args['size_minimum'] < 1:
            raise Exception("Client.py: error: -smin / --size-minimum Must be greater than or equal to 1")

        if args['size_maximum'] > 224:
            raise Exception("Client.py: error: -smax / --size-maximum Must be less than or equal to 224")

        client = Client(args['file'], args['num_requests'], args['size_minimum'], args['size_maximum'], args['address'], args['port'])
        client.start_client()
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
