import socket
from constants import target_port, chunk_size
import os
import flet as ft

class Sender:
    def __init__(self):
        self.__target_port = target_port
        self.__chunk_size = chunk_size

    def send_file(self, files, ip, page, snack):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.connect((ip, self.__target_port))
            sender_hostname = socket.gethostname()
            sock.sendall(sender_hostname.encode() + b"\n")

            receiver_hostname = sock.recv(1024).decode().strip()
            snack.content = ft.Text(f'Connected to {receiver_hostname}', color=ft.colors.BLACK)
            if snack not in page.overlay:
                page.overlay.append(snack)
            snack.open = True
            page.update()

            file_names = []
            total_files_size = 0

            for file in files:
                file_names.append(os.path.basename(file))
                total_files_size += os.path.getsize(file)
            
            sock.sendall(f"{file_names}+{total_files_size}".encode() + b"\n")
            acceptance = sock.recv(1024).decode().strip()

            if acceptance == 'accept':
                snack.content = ft.Text('Receiver accepted the file(s).', color=ft.colors.BLACK)
                snack.open = True
                page.update()
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
                            snack.content = ft.Text(f'File transfer completed successfully: {file}.', color=ft.colors.BLACK)
                            snack.open = True
                            page.update()
                # close progressbar
            else:
                snack.content = ft.Text('Receiver declined the file(s).', color=ft.colors.BLACK)
                snack.open = True
                page.update()
