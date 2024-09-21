from constants import broadcast_port
import time
import socket
import platform

class Broadcaster:
    def __init__(self):
        self.__broadcast_port = broadcast_port
        self.__discovered_devices = {}
    
    @staticmethod
    def __get_local_ip():
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))
        local_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        return local_ip

    def listen_for_devices(self, timeout):
        start_time = time.time()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_server:
            udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_server.bind(('', self.__broadcast_port))
            udp_server.settimeout(1)

            my_ip = self.__get_local_ip()

            while True:
                try:
                    if time.time() - start_time > timeout:
                        break
                    message, addr = udp_server.recvfrom(1024)
                    if addr[0] != my_ip:
                        decoded_message = message.decode().split('+')
                        if decoded_message[0] == 'crossshare_by_ansh_thaker':
                            self.__discovered_devices[addr[0]] = (decoded_message[1], decoded_message[2])
                except socket.timeout:
                    continue
        
        return self.__discovered_devices
    
    def broadcast_devices(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_client:
            udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            hostname = socket.gethostname()
            os_name = platform.system()
            while True:
                udp_client.sendto(f'crossshare_by_ansh_thaker+{hostname}+{os_name}'.encode(), ('<broadcast>', self.__broadcast_port))
                time.sleep(1)
    
    def clear_discovered_devices(self):
        self.__discovered_devices.clear()
