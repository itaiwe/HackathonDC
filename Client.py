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
            # udp_socket.bind(("", self.port))
            
            data, address = udp_socket.recvfrom(4096) ##check that
            info = struct.unpack("Ibh", data) ##I-unsigned int 4B b-signed char 1B h-short 2B
            tcp_ip = address[0]
            tcp_socket = self.check_offers(info, tcp_ip)
            if tcp_socket is not None:
                self.game_mode(tcp_socket)
    
    def check_offers(self, info, tcp_ip):
        
        if info[0]==self.cookie and info[1]==self.msg_type:
            server_port=info[2]
            print(f"Received offer from {tcp_ip} attempting to connect...")
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((tcp_ip, server_port))
            massage=f"{self.name}\n".encode() ##check encode type!
            tcp_socket.send(massage)
            return(tcp_socket)
        return(None)
        
    
    def game_mode(self, tcp_socket):
        data=tcp_socket.recv(4096)
        print(data.decode())
        t1=time.time()
        while(time.time()-t1<=10):
            if msvcrt.kbhit():
                key=msvcrt.getch().decode()
                if key.isnumeric():
                    massage=key.encode()##check encode type!
                    tcp_socket.send(massage)
        summary=tcp_socket.recv(4096)
        print(summary.decode())
        tcp_socket.close()
        print("Server disconnected, listening for offer requests...")
        pass
    
magic_cookie, msg_type, port = 0xabcddcba, 0x2, 13117
team_name = '""'
client = Client(team_name, magic_cookie, msg_type, port)
client.run_client()