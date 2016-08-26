import socket 
import sys
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('hotspot.cfg')
ip = config.get('server','ip')
port = config.getint('server','port')
sock = None
	
try:
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# set socket to non-blocking 
#	sock.setblocking(0)
	server_address = (ip,port)
	sock.connect(server_address)
	while(1):
# 16 is data size (argument)
		data = sock.recv(16)
		print("Server Data: " + data)
finally:
	sock.close() 
