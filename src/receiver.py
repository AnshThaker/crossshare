from constants import listening_port, chunk_size
import socket
import ast

class Receiver:
    def __init__(self):
        self.__listening_port = listening_port
        self.__chunk_size = chunk_size

    def receive_file(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('0.0.0.0', self.__listening_port))
            server.listen(5)
            print(f'Listening on port {self.__listening_port}...')

            while True:
                conn, addr = server.accept()
                with conn:
                    sender_hostname = conn.recv(1024).decode().strip()
                    receiver_hostname = socket.gethostname()
                    conn.sendall(receiver_hostname.encode() + b"\n")

                    files_info = conn.recv(1024).decode().strip()
                    file_names, total_file_size = files_info.split('+')
                    file_names = ast.literal_eval(file_names)
                    total_file_size = int(total_file_size)
                    print(f"Connection from {sender_hostname}")
                    for index, file_name in enumerate(file_names):
                        print(f'File {index + 1}: {file_name}')
                    print(f"Total Size: {total_file_size} bytes")

                    accept_or_decline = input(f'Would you like to receive the file(s)? [a/d] ').lower()
                    print(accept_or_decline)

                    if accept_or_decline == 'a':
                        conn.sendall(b'accept')
                        # initialise progressbar

                        for file_name in file_names:
                            with open(file_name, 'wb') as file:
                                while True:
                                    data = conn.recv(self.__chunk_size)
                                    if data.endswith(b'<END>'):
                                        data = data[:-5]
                                        file.write(data)
                                        # update progressbar
                                        break
                                    file.write(data)
                                    # update progressbar
                            print(f'Received file from {sender_hostname}: {file_name}')
                            conn.sendall(b'completed')
                        # close progressbar
                    else:
                        conn.sendall(b'decline')
                        print(f'File(s) declined.')
