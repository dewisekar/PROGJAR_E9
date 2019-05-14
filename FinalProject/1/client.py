import socket
import select
import sys
import msvcrt

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = "127.0.0.1"
Port = 8081
server.connect((IP_address, Port))

while True:
	socket_list = [server]
	read_socket, write_socket, error_socket = select.select(socket_list, [], [], 1)
	if msvcrt.kbhit(): read_socket.append(sys.stdin)

	for socks in read_socket:
		if socks == server:
			message = socks.recv(2048)
			if '~^^^^^~' in message:
				message = message.split('~^^^^^~')
				file = message[0].split('\n')
				file = file[0]
				print 'recv content ' + str(file)
				message = message[-1]
				# message = message[-1].decode('utf-8')
				f = open(file, "ab")
				f.write(message)
				f.close()
			else:
				print message
		else:
			message = sys.stdin.readline()
			if "SEND" in message:
				file = ''
				mes = []
				message.split('SEND')
				print '<You>file broadcast sending: ' + message[5:-1]
				filename = str(message[5:-1])
				file += filename + "~^^^^^~"
				# f = open(file, 'rb')
				length = 2048-len(file)
				with open(filename, 'rb') as f:
					for res in iter(lambda: f.read(length), ''):
						file = ''
						file += filename + "~^^^^^~"
						file += res
						message = file
						server.send(message)
				f.close()
			else:
				server.send(message)
				sys.stdout.write("<You>")
				sys.stdout.write(message)
			sys.stdout.flush()

server.close()