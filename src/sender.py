import socket
from constants import target_port, chunk_size
import os

class Sender:
    def __init__(self):
        self.__target_port = target_port
        self.__chunk_size = chunk_size

    def send_file(self, files, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.connect((ip, self.__target_port))
            sender_hostname = socket.gethostname()
            sock.sendall(sender_hostname.encode() + b"\n")

            receiver_hostname = sock.recv(1024).decode().strip()
            print(f'Connected to {receiver_hostname}')

            file_names = []
            total_files_size = 0

            for file in files:
                file_names.append(os.path.basename(file))
                total_files_size += os.path.getsize(file)
            
            sock.sendall(f"{file_names}+{total_files_size}".encode() + b"\n")
            acceptance = sock.recv(1024).decode().strip()

            if acceptance == 'accept':
                print(f'Receiver accepted the file(s).')
                # initialise progressbar
                for file in files:
                    with open(file, 'rb') as to_send:
                        while True:
                            file_data = to_send.read(self.__chunk_size)
                            if not file_data:
                                break
                            sock.sendall(file_data)
                            # update progressbar
                        sock.sendall(b'<END>')
                        completed = sock.recv(1024).decode().strip()
                        if completed:
                            print(f'File transfer completed successfully: {file}.')
                # close progressbar
            else:
                print(f"Receiver declined the file(s).")
