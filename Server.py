import socket
import struct
import threading
import time
from datetime import datetime
import scapy.all as scapy
import random


class server:
    def __init__(self): #maybe add eth and set to eth1 or eth2 when creating server
        self.port = 13117
        self.cookie = 0xabcddcba
        self.msg_type = 0x2
        self.server_ip = scapy.get_if_addr(scapy.conf.iface) #scapy.conf.iface
        self.tcp_port = 25000
        self.users = 0
        self.equations = [("3+3","6"),("3+2","5"),("1+2","3"),("7+1","8"),("1+1","2")]
        self.flag = False
        self.message = ""
        self.mutex = threading.Lock()
        self.team_names = []
        self.sockets=[]
        
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
            t = threading.Thread(target=self.send_udp_offer, args=(self.tcp_port, udp_socket))
            t.start()
            self.team_names, self.sockets = self.listen_tcp(tcp_socket)
            time.sleep(10)
            question, answer = random.choice(self.equations)
            message = f"""Welcome to Quick Maths.
            Player 1: {self.team_names[0]}Player 2: {self.team_names[1]}==
            Please answer the following question as fast as you can:
            How much is: {question}?""".encode() #add formula here
            self.message = f'Game over!\nThe correct answer was {answer}!\n\nGame ended in a draw!'
            thread_player1 = threading.Thread(target=self.game_mode, args=(self.sockets[0], message, answer, 0))
            thread_player2 = threading.Thread(target=self.game_mode, args=(self.sockets[1], message, answer, 1))
            thread_game=threading.Thread(target=self.count_game)
            thread_player1.start()
            thread_player2.start()
            thread_game.start()
            thread_player1.join()
            thread_player2.join()
            thread_game.join()
            self.sockets[0].close() #check that
            self.sockets[1].close() #check that
            print("Game over, sending out offer requests...")
                
            
    def listen_tcp(self, tcp_socket):
        team_names, sockets = [], []
        tcp_socket.listen(2)
        while self.users < 2:
            try:
                team_socket, _ = tcp_socket.accept()
                team_socket.settimeout(1)
                sockets.append(team_socket)
                team_name = team_socket.recv(2048).decode()
                team_names.append(team_name)
                self.users += 1
            except socket.timeout:
                break 
        return team_names, sockets
    
    
    def game_mode(self, player_socket, welcome_message, answer, idx):
        player_socket.send(welcome_message)
        # t1 = time.time()
        # while time.time() - t1 <= 10 or self.flag:
        try:
            data = player_socket.recv(2048).decode()
            self.mutex.acquire(1)
            if data == answer:
                self.message = f'Game over!\nThe correct answer was {answer}!\n\nCongratulations to the winner: {self.team_names[idx]}'.strip('\n')
            else:
                self.message = f'Game over!\nThe correct answer was {answer}!\n\nCongratulations to the winner: {self.team_names[abs(idx - 1)]}'.strip('\n')
            self.flag = True
            self.mutex.release()
        except:
            pass
        player_socket.send(self.message)

    def count_game(self):
        t1 = time.time()
        while time.time() - t1 <= 10:
            if self.flag:
                break
        for s in self.sockets:
            s.setbloking(False)

s=server()
s.run_server()
