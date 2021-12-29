import socket
import struct
import threading
import time
from datetime import datetime
import scapy.all as scapy
import random
import multiprocessing as mul_proc
from colors import colors

class server:
    def __init__(self, dev): #maybe add eth and set to eth1 or eth2 when creating server
        """creating server

        Args:
            dev ([bool]): [checking on what eth we are]
        """
        self.port = 13117
        self.cookie = 0xabcddcba
        self.msg_type = 0x2
        self.server_ip = scapy.get_if_addr("eth1" if dev else "eth2") #scapy.conf.iface
        self.tcp_port = 25000
        self.users = 0
        self.equations = [("3+3","6"),("3+2","5"),("1+2","3"),("7+1","8"),("1+1","2"),("9^0.5","3"),("3+10-5","8"),("(10*3-15)/5","3"),("(123*5+3)*(23-12+6^3)*(12-3*4)","0"),("|5-8|","3"),("100/10-4","6"),("5+3-2+1","7"),("(123-23-1)/11","9"),("2-1","1"),("18/3","6"),("(1/3)*9","3"),("(94/2+1)/8","6"),("13-6","7"),("45/9","5"),("-10*(-2)-19","1"),("4+3-1","6"),("3*2+1^0","7"),("0.01*100","1")]
        self.flag = False
        self.message = ["",""]
        self.mutex = threading.Lock()
        self.team_names = []
        self.sockets = []

    def send_udp_offer(self, tcp_port, udp_socket:socket):
        """sending udp offers for clients to join

        Args:
            tcp_port ([int]): [server's tcp port]
            udp_socket ([socket]): [server's udp socket]
        """
        while self.users < 2:
            format = "IbH"
            offer = struct.pack(format, self.cookie, self.msg_type, tcp_port)
            udp_socket.sendto(offer, ('<broadcast>', self.port)) # sending broadcast message to all possible clients
            time.sleep(1)
            
    def run_server(self):
        """
        main function to run server
        """
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # setting UDP socket
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enabling option to broadcast for ip address
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # enabling reusability of ports
        udp_socket.bind((self.server_ip, self.port)) # binding server to ip and port
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # setting TCP socket
        tcp_socket.bind((self.server_ip, self.tcp_port))
        udp_socket.settimeout(10)
        tcp_socket.settimeout(10)
        print(colors.front.BOLD+colors.front.UNDERLINE+colors.CYAN+"Server started,"+colors.ENDC+colors.CYAN+ "listening on IP address"+colors.back.RED+colors.GREEN+f"{self.server_ip}"+colors.ENDC)
        while True:
            t = threading.Thread(target=self.send_udp_offer, args=(self.tcp_port, udp_socket)) # thread for sending offers
            t.start()
            self.team_names, self.sockets = self.listen_tcp(tcp_socket) # getting team names and sockets connecting clients
            time.sleep(10)
            question, answer = random.choice(self.equations)
            message = f"""Welcome to Quick Maths.\nPlayer 1: {self.team_names[0]}Player 2: {self.team_names[1]}==\nPlease answer the following question as fast as you can:\nHow much is: {question}?""".encode() 
            for i in len(self.message):
                self.message[i] = f'Game over!\nThe correct answer was {answer}!\n\nGame ended in a draw!'
            thread_player1 = threading.Thread(target=self.game_mode, args=(self.sockets[0], message, answer, 0))
            thread_player2 = threading.Thread(target=self.game_mode, args=(self.sockets[1], message, answer, 1))
            thread_game=mul_proc.Process(target=self.count_game)
            thread_player1.start()
            thread_player2.start()
            thread_game.start()
            thread_player1.join()
            thread_player2.join()
            if self.flag: # if clients already answered before 10 seconds have passed, terminate process
                thread_game.terminate()
            thread_game.join()
            self.sockets[0].close() 
            self.sockets[1].close() 
            self.users = 0
            self.flag = False
            self.message=["",""] # messages for different users
            print(colors.front.BOLD+colors.front.UNDERLINE+colors.YELLOW+"Game over,"+colors.ENDC+colors.YELLOW+" sending out offer requests..."+colors.ENDC)
                
            
    def listen_tcp(self, tcp_socket):
        """connecting clients to server

        Args:
            tcp_socket ([socket]): [socket of server]

        Returns:
            [two lists]: [team names and sockets]
        """
        team_names, sockets = [], []
        tcp_socket.listen(2)
        tcp_socket.settimeout(10)
        while self.users < 2:
            try:
                team_socket, _ = tcp_socket.accept()
                team_socket.settimeout(1)
                sockets.append(team_socket)
                team_name = team_socket.recv(2048).decode()
                team_names.append(team_name)
                self.users += 1
            except socket.timeout:
                continue 
        return team_names, sockets
    
    
    def game_mode(self, player_socket, welcome_message, answer, idx):
        """main game function of server

        Args:
            player_socket ([socket]): [socket connecting player]
            welcome_message ([bytes]): [welcome message]
            answer ([str]): [answer of question]
            idx ([int]): [index of player]
        """
        player_socket.send(welcome_message)
        t1=time.time()
        while time.time()-t1<=10 and not self.flag:
            try:
                player_socket.settimeout(0.1)
                data = player_socket.recv(2048).decode()
                self.mutex.acquire(1) #allowing only first answer 
                if data == answer and not self.flag:
                    self.message[idx] = f'Game over!\nThe correct answer was {answer}!\n\nCongratulations You Won!'
                    self.message[abs(idx - 1)] = f'Game over!\nsadly you lost!\nThe correct answer was {answer}!\n\nCongratulations to the winner: {self.team_names[idx]}'.strip('\n')
                elif data != answer and not self.flag:
                    self.message[abs(idx - 1)] = f'Game over!\nThe correct answer was {answer}!\n\nCongratulations You Won!'
                    self.message[idx] = f'Game over!\nsadly you lost!\nThe correct answer was {answer}!\n\nCongratulations to the winner: {self.team_names[idx]}'.strip('\n')
                self.flag = True
                self.mutex.release()
            except:
                pass
        try:
            player_socket.send(self.message[idx].encode()) #sends respective summary message to players
        except:
            pass

    def count_game(self):
        """sets timer for game
        """
        time.sleep(10)
        self.flag = True

s = server(dev=False)
s.run_server()
