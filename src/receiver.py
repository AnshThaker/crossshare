import constants
import socket
import ast
import flet as ft
import time
import math
import os
import platform

class Receiver:
    def __init__(self):
        self.__listening_port = constants.listening_port
        self.__chunk_size = constants.chunk_size
        self.__acceptance = None

    @staticmethod
    def __remove_receiving_error_dialog(page, dialog):
        dialog.open = False
        page.update()
    
    @staticmethod
    def __convert_size(size_bytes):
        if size_bytes == 0:
            return '0 bytes'
        size_name = ('bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        index = int(math.floor(math.log(size_bytes, 1024)))
        power = math.pow(1024, index)
        size = round(size_bytes / power, 2)
        return '%s %s' % (size, size_name[index])
    
    @staticmethod
    def __get_downloads_folder():
        if platform.system() == constants.os_windows:
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        elif platform.system() == constants.os_mac:
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        elif platform.system() == 'Linux':
            if os.path.exists('/storage/emulated/0/Documents'):
                return '/storage/emulated/0/Documents'
            elif os.path.exists('/sdcard/Documents'):
                return '/sdcard/Documents'
            else:
                return os.getcwd()
    
    def __handle_accept(self, e):
        self.__acceptance = 'a'
    
    def __handle_decline(self, e):
        self.__acceptance = 'd'

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

                        files_list_view = ft.ListView(height=300)
                        files_list_view.controls.append(ft.Text(f'Would you like to receive these file(s) from {sender_hostname}?', size=14))
                        files_list_view.controls.append(ft.Divider())
                        for index, file_name in enumerate(file_names):
                            files_list_view.controls.append(ft.Text(f'File {index + 1}: {file_name}', size=12))
                        files_list_view.controls.append(ft.Divider())
                        files_list_view.controls.append(ft.Text(f'Total Size: {self.__convert_size(total_file_size)}', size=14))

                        accept_button = ft.ElevatedButton('Accept', icon='check', on_click=self.__handle_accept)
                        decline_button = ft.ElevatedButton('Decline', icon='close', on_click=self.__handle_decline)

                        acceptance_dialog = ft.AlertDialog(
                            title=ft.Text('Incoming file(s)'),
                            modal=True,
                            content=files_list_view,
                            actions=[accept_button, decline_button],
                            actions_alignment=ft.MainAxisAlignment.END
                        )

                        page.overlay.append(acceptance_dialog)
                        acceptance_dialog.open = True
                        page.update()

                        while not self.__acceptance:
                            time.sleep(.1)

                        if self.__acceptance == 'a':
                            receiving_file_text = ft.Text('Receiving files...', size=14)
                            receiving_files_progressbar = ft.ProgressBar(width=400, color='#3478f5', bgcolor='#eeeeee', value=0)
                            receiving_files_col = ft.Column(
                                [
                                    receiving_file_text,
                                    receiving_files_progressbar,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                tight=True
                            )

                            acceptance_dialog.content = receiving_files_col
                            acceptance_dialog.actions = None
                            acceptance_dialog.actions_alignment = None
                            page.update()

                            downloads_dir = self.__get_downloads_folder()

                            conn.sendall(b'accept')

                            for file_name in file_names:
                                receiving_file_text.value = f'Receiving file: {file_name}'
                                page.update()

                                file_path = os.path.join(downloads_dir, file_name)

                                with open(file_path, 'wb') as file:
                                    while True:
                                        data = conn.recv(self.__chunk_size)
                                        if data.endswith(b'<END>'):
                                            data = data[:-5]
                                            file.write(data)
                                            receiving_files_progressbar.value += (len(data)) / (total_file_size)
                                            page.update()
                                            break
                                        file.write(data)
                                        receiving_files_progressbar.value += (len(data)) / (total_file_size)
                                        page.update()
                                snack.content = ft.Text(f'Received file from {sender_hostname}: {file_name}', color=ft.colors.BLACK)
                                snack.open = True
                                page.update()
                                conn.sendall(b'completed')
                            acceptance_dialog.open = False
                            page.update()
                        elif self.__acceptance == 'd':
                            conn.sendall(b'decline')
                            acceptance_dialog.open = False
                            snack.content = ft.Text('File(s) declined.', color=ft.colors.BLACK)
                            snack.open = True
                            page.update()
                        
                        self.__acceptance = None
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
