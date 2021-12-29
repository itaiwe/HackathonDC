import socket
import struct
import time
from datetime import datetime
import getch
import multiprocessing as mul_proc
from colors import colors

class Client:
    def __init__(self, team):
        self.name = team
        self.cookie = 0xabcddcba
        self.msg_type = 0x2
        self.port = 13117
        self.flag = True
    
    def run_client(self):
        """Main function of Client
        """
        print(colors.front.BOLD+colors.front.UNDERLINE+colors.LIGHTGREEN+"Client started,"+colors.ENDC+colors.LIGHTGREEN+" listening for offer requests..."+colors.ENDC)
        while True:
            self.flag=True
            # creating udp socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # setting UDP socket
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # enabling option to broadcast for ip address
            udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT, 1) # enabling reusability of port for self check
            udp_socket.bind(("172.99.255.255", self.port))
            
            data, address = udp_socket.recvfrom(2048) # receiving packet for connecting to TCP
            try:
                info = struct.unpack("IbH", data) ##I-unsigned int 4B b-signed char 1B h-short 2B
                tcp_ip = address[0]
                tcp_socket = self.check_offers(info, tcp_ip)
                if tcp_socket is not None:
                    self.game_mode(tcp_socket)
            except:
                continue
    
    def check_offers(self, info, tcp_ip):
        """Checking UDP offers sent from server and tries to connect

        Args:
            info ([tuple]): [packet sent from server]
            tcp_ip ([str]): [IP of server]
        """
        if info[0]==self.cookie and info[1]==self.msg_type:
            server_port=info[2]
            print(colors.LIGHTBLUE+"Received offer from "+colors.front.BOLD+colors.ORANGE+f"{tcp_ip}"+colors.ENDC+colors.LIGHTBLUE+" attempting to connect..."+colors.ENDC)
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creating socket for TCP connection
            tcp_socket.connect((tcp_ip, server_port)) # connecting to server
            massage=f"{self.name}\n".encode() #sending name
            tcp_socket.send(massage)
            return tcp_socket
        return None
        
    
    def game_mode(self, tcp_socket):
        """Main game function

        Args:
            tcp_socket ([socket]): [Client's socket for game]
        """
        data = tcp_socket.recv(2048)
        print(colors.GREEN+data.decode()+colors.ENDC)
        p = mul_proc.Process(target=self.get_user_key,args=(tcp_socket,)) # starting process for getch so we will be able to stop if other client answered and finished the game
        p.start()
        while self.flag:
            try:
                tcp_socket.settimeout(0.1)
                summary=tcp_socket.recv(2048) # trying to recieve summary message from server
                self.flag=False
            except:
                pass
        p.terminate() # killing the process if summary was sent
        p.join()
        print(colors.PURPLE+summary.decode()+colors.ENDC)
        tcp_socket.close()
        print(colors.front.BOLD+colors.front.UNDERLINE+colors.RED+"Server disconnected,"+colors.ENDC+colors.YELLOW+" listening for offer requests..."+colors.ENDC)
        
    
    def get_user_key(self,tcp_socket):
        key=getch.getch() #blocks code and waits for key
        massage=key.encode()
        tcp_socket.send(massage)


team_name = 'sucket for pain'
client = Client(team_name)
client.run_client()
