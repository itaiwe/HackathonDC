import socket
import struct
import time
from datetime import datetime
import msvcrt

class Client:
    def __init__(self, team, cookie, msg_type, port):
        self.name = team
        self.cookie = cookie
        self.msg_type = msg_type
        self.port = port
    
    def run_client(self):
        while True:
            print("Client started, listening for offer requests...")
            # creating udp socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # setting UDP socket
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enabling option to broadcast for ip address
            udp_socket.bind(("", self.port))
            
            data, address = udp_socket.recvfrom(2048) ##check that
            info = struct.unpack("Ibh", data) ##check that
            tcp_ip = address[0]
            tcp_socket = self.check_offers(info, tcp_ip)
            if tcp_socket is not None:
                self.game_mode(tcp_socket)
    
    def check_offers(self, info, tcp_ip):
        pass
    
    def game_mode(self, tcp_socket):
        pass
    
magic_cookie, msg_type, port = 0xabcddcba, 0x2, 13117
team_name = ""
client = Client(team_name, magic_cookie, msg_type, port)
client.run_client()