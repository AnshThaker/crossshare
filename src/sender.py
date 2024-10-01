import socket
from constants import target_port, chunk_size
import os
import flet as ft

class Sender:
    def __init__(self):
        self.__target_port = target_port
        self.__chunk_size = chunk_size

    def send_file(self, files, ip, page, snack, send_dialog):
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

            waiting_for_response_text = ft.Text('Waiting for response...', size=14)
            waiting_for_response_progressbar = ft.ProgressBar(width=400, color='#3478f5', bgcolor='#eeeeee')
            waiting_for_response_col = ft.Column(
                [
                    waiting_for_response_text,
                    waiting_for_response_progressbar,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True
            )

            send_dialog.content = waiting_for_response_col
            send_dialog.actions = None
            send_dialog.actions_alignment = None
            page.update()

            acceptance = sock.recv(1024).decode().strip()

            if acceptance == 'accept':
                sending_file_text = ft.Text('Sending files...', size=14)
                sending_files_progressbar = ft.ProgressBar(width=400, color='#3478f5', bgcolor='#eeeeee', value=0)
                sending_files_col = ft.Column(
                    [
                        sending_file_text,
                        sending_files_progressbar,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True
                )

                send_dialog.content = sending_files_col
                page.update()

                for file in files:
                    sending_file_text.value = f'Sending file: {os.path.basename(file)}'
                    page.update()
                    with open(file, 'rb') as to_send:
                        while True:
                            file_data = to_send.read(self.__chunk_size)
                            if not file_data:
                                break
                            sock.sendall(file_data)
                            sending_files_progressbar.value += (len(file_data)) / (total_files_size)
                            page.update()
                        sock.sendall(b'<END>')
                        completed = sock.recv(1024).decode().strip()
                        if completed:
                            snack.content = ft.Text(f'File transfer completed successfully: {file}.', color=ft.colors.BLACK)
                            snack.open = True
                            page.update()
                send_dialog.open = False
                page.update()
            else:
                send_dialog.open = False
                page.update()
                snack.content = ft.Text('Receiver declined the file(s).', color=ft.colors.BLACK)
                snack.open = True
                page.update()
