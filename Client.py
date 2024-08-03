import socket


class Client:
    def __init__(self, local_host='127.0.0.1', server_port=5000):
        self.local_host = local_host
        self.server_port = server_port

    def display_commands(self):
        print('\n==== Please Choose From the Following Commands ====')
        print('MSGGET - Get message of the day')
        print('MSGSTORE - Update message of the day')
        print('QUIT - Close the client')
        print('SHUTDOWN - Shutdown the server, password required\n')

    def start_program(self, tcp_socket):
        while True:
            self.display_commands()

            # read user input
            user_input = input('Enter a command: ')

            # Send command to server and handle the command on the client side appropriately
            tcp_socket.send(user_input.encode('utf-8'))

            # Also display initial response
            response = tcp_socket.recv(1024).decode('utf-8')
            print(f'Received from server: {response}')

            # handle user's choice based on command chosen
            match user_input.upper():
                case "MSGGET":
                    # Initial response suffices for this command so pass is appropriately used here
                    pass
                case "MSGSTORE":
                    user_input = input('New message: ')

                    tcp_socket.send(user_input.encode('utf-8'))

                    response = tcp_socket.recv(1024).decode('utf-8')
                    print(f'Received from server: {response}')
                case "QUIT":
                    tcp_socket.close()
                    break
                case "SHUTDOWN":
                    user_input = input('Enter password: ')

                    tcp_socket.send(user_input.encode('utf-8'))

                    response = tcp_socket.recv(1024).decode('utf-8')
                    print(f'Received from server: {response}')

                    # if response returns a 200, close the client as well. Use substring to read status code
                    if response[:3] == '200':
                        tcp_socket.close()
                        break
                case _:
                    continue

    def start_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            # Ask for client to enter ip address for the local host
            print('Enter an ip address or type the word \"default\" for the default client ip address:')
            self.local_host = input('Enter IP Address: ')

            if self.local_host.upper() == 'DEFAULT':
                self.local_host = '127.0.0.1'

            # connect to local host
            tcp_socket.connect((self.local_host, self.server_port))
            self.start_program(tcp_socket)


if __name__ == '__main__':
    client = Client()
    client.start_client()