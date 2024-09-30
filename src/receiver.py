from constants import listening_port, chunk_size
import socket
import ast
import flet as ft

class Receiver:
    def __init__(self):
        self.__listening_port = listening_port
        self.__chunk_size = chunk_size

    @staticmethod
    def __remove_receiving_error_dialog(page, dialog):
        dialog.open = False
        page.update()

    def receive_file(self, page, snack):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('0.0.0.0', self.__listening_port))
            server.listen(5)

            while True:
                try:
                    conn, addr = server.accept()
                    with conn:
                        sender_hostname = conn.recv(1024).decode().strip()
                        receiver_hostname = socket.gethostname()
                        conn.sendall(receiver_hostname.encode() + b"\n")

                        files_info = conn.recv(1024).decode().strip()
                        file_names, total_file_size = files_info.split('+')
                        file_names = ast.literal_eval(file_names)
                        total_file_size = int(total_file_size)
                        snack.content = ft.Text(f'Connection from {sender_hostname}', color=ft.colors.BLACK)
                        if snack not in page.overlay:
                            page.overlay.append(snack)
                        snack.open = True
                        page.update()
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
                                snack.content = ft.Text(f'Received file from {sender_hostname}: {file_name}', color=ft.colors.BLACK)
                                snack.open = True
                                page.update()
                                conn.sendall(b'completed')
                            # close progressbar
                        else:
                            conn.sendall(b'decline')
                            snack.content = ft.Text('File(s) declined.', color=ft.colors.BLACK)
                            snack.open = True
                            page.update()
                except Exception as error:
                    receiving_error_dialog = ft.AlertDialog(
                        title=ft.Text('Error receiving file(s)'),
                        content=ft.Text(error),
                        on_dismiss=lambda _: self.__remove_receiving_error_dialog(page, receiving_error_dialog),
                    )
                    page.overlay.clear()
                    page.overlay.append(receiving_error_dialog)
                    receiving_error_dialog.open = True
                    page.update()
