import socket
import struct
import threading
import time
from datetime import datetime
import scapy.all as scapy

def __init__(self, port_udp, cookie, msg_type):
    self.port = port_udp
    self.cookie = cookie
    self.msg_type = msg_type
    self.server_ip = scapy.get_if_addr(scapy.conf.iface)
    
def send_udp_offer(self, tcp_port, udp_socket):
    for _ in range(10):
        format = "Ibh"
        offer = struct.pack(format, self.cookie, self.msg_type, tcp_port)
        udp_socket.send(offer, ('<broadcast>', self.port_udp))
        time.sleep(1)