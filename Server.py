import socket
import struct
import threading
import time
from datetime import datetime
import scapy.all as scapy
import random


class server:
    def __init__(self, port_udp, cookie, msg_type, tcp_port):
        self.port = port_udp
        self.cookie = cookie
        self.msg_type = msg_type
        self.server_ip = scapy.get_if_addr(scapy.conf.iface)
        self.tcp_port = tcp_port
        self.users = 0
        self.equations = []
        self.flag = False
        self.message = ""
        self.mutex = threading.Lock()
        self.team_names = []
        
    def send_udp_offer(self, tcp_port, udp_socket:socket):
        while self.users < 2:
            format = "Ibh"
            offer = struct.pack(format, self.cookie, self.msg_type, tcp_port)
            udp_socket.sendto(offer, ('<broadcast>', self.port_udp))
            time.sleep(1)
            
    def run_server(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # setting UDP socket
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enabling option to broadcast for ip address
        udp_socket.bind((self.server_ip, self.port))
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # setting TCP socket
        tcp_socket.bind((self.server_ip, self.port))
        udp_socket.settimeout(10)
        tcp_socket.settimeout(10)
        while True:
            print(f"Server started, listening on IP address {self.server_ip}")
            t = threading.Thread(self.send_udp_offer, args=(self.tcp_port, udp_socket))
            t.start()
            self.team_names, sockets = self.listen_tcp(tcp_socket)
            time.sleep(10)
            question, answer = random.choice(self.equations)
            message = f"""Welcome to Quick Maths.
            Player 1: {self.team_names[0]}Player 2: {self.team_names[1]}==
            Please answer the following question as fast as you can:
            How much is: {question}?""".encode() #add formula here
            thread_player1 = threading.Thread(self.game_mode, args=(sockets[0], message, answer, 0))
            thread_player2 = threading.Thread(self.game_mode, args=(sockets[1], message, answer, 1))
            thread_player1.start()
            thread_player2.start()
            thread_player1.join()
            thread_player2.join()
            sockets[0].close() #check that
            sockets[1].close() #check that
            print("Game over, sending out offer requests...")
                
            
    def listen_tcp(self, tcp_socket):
        team_names, sockets = [], []
        tcp_socket.listen(2)
        while self.users < 2:
            try:
                team_socket, _ = tcp_socket.accept()
                sockets.append(team_socket)
                team_name = team_socket.recv(4096).decode()
                team_names.append(team_name)
                self.users += 1
            except socket.timeout:
                break 
        return team_names, sockets
    
    
    def game_mode(self, player_socket, welcome_message, answer, idx):
        player_socket.send(welcome_message)
        t1 = time.time()
        while time.time() - t1 <= 10 or self.flag:
            data = player_socket.recv(4096).decode()
            self.mutex.acquire(1)
            if data == answer:
                self.message = f'Game over!\nThe correct answer was {answer}!\n\nCongratulations to the winner: {self.team_names[idx]}'.strip('\n')
            else:
                self.message = f'Game over!\nThe correct answer was {answer}!\n\nCongratulations to the winner: {self.team_names[abs(idx - 1)]}'.strip('\n')
            self.flag = True
            self.mutex.release()
        if not self.flag:
            self.message = f'Game over!\nThe correct answer was {answer}!\n\nGame ended in a draw!'
        player_socket.send(self.message)
    