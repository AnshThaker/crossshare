import flet as ft
import threading
from broadcaster import Broadcaster
from sender import Sender
from receiver import Receiver
import constants

broadcaster = Broadcaster()
sender = Sender()
receiver = Receiver()

def main(page: ft.Page):
    page.title = 'CrossShare'

    snack = ft.SnackBar(ft.Text('CrossShare by Ansh Thaker'), duration=3000, bgcolor=ft.colors.WHITE)

    broadcast_thread = threading.Thread(target=broadcaster.broadcast_devices)
    broadcast_thread.start()
    receive_thread = threading.Thread(target=receiver.receive_file, args=(page, snack,))
    receive_thread.start()

    def file_dialog_result(e: ft.FilePickerResultEvent, ip, file_dialog):
        page.overlay.remove(file_dialog)
        page.update()
        if e.files:
            file_paths = tuple(file.path for file in e.files)
            try:
                sender.send_file(file_paths, ip, page, snack)
            except Exception as error:
                global sending_error_dialog
                sending_error_dialog = ft.AlertDialog(
                    title=ft.Text('Error sending file(s)'),
                    content=ft.Text(error),
                    on_dismiss=remove_sending_error_dialog,
                )
                page.overlay.clear()
                send_dialog.open = False
                page.overlay.append(sending_error_dialog)
                sending_error_dialog.open = True
                page.update()

    def open_file_dialog(e, ip):
        file_dialog = ft.FilePicker(on_result=lambda e: file_dialog_result(e, ip, file_dialog))
        page.overlay.append(file_dialog)
        page.update()
        file_dialog.pick_files(allow_multiple=True, dialog_title='Select File(s) To Send')

    def close_send_dialog(e):
        send_dialog.open = False
        page.update()

    def remove_sending_error_dialog(e):
        sending_error_dialog.open = False
        page.update()

    def remove_error_dialog(e):
        error_dialog.open = False
        page.update()
    
    def get_icon_for_os(os_name):
        if os_name == constants.os_windows:
            return ft.icons.WINDOW
        elif os_name == constants.os_mac:
            return ft.icons.APPLE
        elif os_name == constants.os_android:
            return ft.icons.ANDROID
        else:
            return ft.icons.DEVICE_UNKNOWN

    def send(e):
        global send_dialog

        broadcaster.clear_discovered_devices()

        searching_progress_ring = ft.ProgressRing(color='#3478f5')
        searching_text = ft.Text('Searching for available devices...', size=14)
        searching_row = ft.Row(
            [
                searching_progress_ring,
                searching_text,
            ],
            alignment = ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        no_devices_text = ft.Text('No devices online.', size=16)
        close_send_dialog_button = ft.ElevatedButton('Close', icon='close_rounded', on_click=close_send_dialog)
        refresh_send_dialog_button = ft.ElevatedButton('Refresh', icon='refresh', on_click=send)

        devices_list_view = ft.ListView(height=300)

        send_dialog = ft.AlertDialog(
            title=ft.Text("Send file(s)"),
            modal=True,
            content=searching_row,
        )

        page.overlay.clear()
        page.overlay.append(send_dialog)
        send_dialog.open = True
        page.update()
        
        # for i in range(20):
        #     devices_list_view.controls.append(ft.ListTile(title=ft.Text('Test'), subtitle=ft.Text('Secondary test'), mouse_cursor=ft.MouseCursor.CLICK, leading=ft.Icon(ft.icons.LAPTOP_WINDOWS_ROUNDED), hover_color=ft.colors.GREY))
        #     send_dialog.content = devices_list_view
        #     send_dialog.actions = [close_send_dialog_button]
        #     send_dialog.actions_alignment = ft.MainAxisAlignment.END
        #     page.update()
        
        try:
            devices = broadcaster.listen_for_devices(5)
            if devices:
                for ip, (hostname, os_name) in devices.items():
                    icon = get_icon_for_os(os_name)
                    devices_list_view.controls.append(ft.ListTile(title=ft.Text(hostname), subtitle=ft.Text(ip), mouse_cursor=ft.MouseCursor.CLICK, leading=ft.Icon(icon), on_click=lambda e: open_file_dialog(e, ip)))
                send_dialog.content = devices_list_view
                send_dialog.actions = [close_send_dialog_button, refresh_send_dialog_button]
                send_dialog.actions_alignment = ft.MainAxisAlignment.END
                page.update()
            else:
                send_dialog.content = no_devices_text
                send_dialog.actions = [close_send_dialog_button, refresh_send_dialog_button]
                send_dialog.actions_alignment = ft.MainAxisAlignment.END
                page.update()
        except Exception as error:
            global error_dialog
            error_dialog = ft.AlertDialog(
                title=ft.Text('Error searching for devices'),
                content=ft.Text(error),
                on_dismiss=remove_error_dialog,
            )
            page.overlay.clear()
            send_dialog.open = False
            page.overlay.append(error_dialog)
            error_dialog.open = True
            page.update()
    
    
    send_button = ft.ElevatedButton('Send', icon='send_rounded', on_click=send)
    icon = ft.Image(
        src='./icon.png',
        width=100,
        height=100,
        fit=ft.ImageFit.CONTAIN,
    )
    text = ft.Text('CrossShare', size=25)

    icon_row = ft.Row(
        [icon],
        alignment=ft.MainAxisAlignment.CENTER
    )
    text_row = ft.Row(
        [text],
        alignment=ft.MainAxisAlignment.CENTER
    )
    space_after_text = ft.Container(padding=ft.Padding(0, 5, 0, 0))
    button_row = ft.Row(
        [send_button],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    col = ft.Column(
        [
            icon_row,
            text_row,
            space_after_text,
            button_row,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )

    page.add(col)

ft.app(main, assets_dir='assets')
