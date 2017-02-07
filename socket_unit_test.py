import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("10.32.56.2", 5800)
sock.connect(server_address)

print "Socket connected to host " + str(host) + " on port " + str(port)

try:
	message = "Hello world!"
	print "Sending 'Hello world!'"
	sock.sendall(message)
	
	amount_received = 0
	amount_expected = 0
	
	while amount_received < amount_expected:
		data = sock.recv(16)
		amount_received += len(data)
		print "Received " + str(data)

finally:
	print "Closing socket"
	sock.close()
