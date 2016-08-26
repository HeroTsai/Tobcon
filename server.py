import socket
import sys

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_address = ('127.0.0.1',20001)
sock.bind(server_address)
# max_client number is 10 (argument) 
sock.listen(10)

connection,client_addr = sock.accept()
try:
	while (1):
		data = raw_input("Data to Client: ")
		print(data)
		connection.sendall(data)
finally:
	connection.close()
	sock.close()
