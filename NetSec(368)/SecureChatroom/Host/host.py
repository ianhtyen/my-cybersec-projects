import socket
import threading
import os, sys
import hashlib
import random
from Crypto.Cipher import ARC4

# Host address
HOST = "127.0.0.1"
PORT = 12345

# Have to recreate same key again after encrypt, decrypt due to how it was developed (RC4 Process) from pycryptodome
def createcipher(pwh):
    cipher = ARC4.new(pwh.encode('utf-8'))
    return cipher

def encrypt(cipher, plaintext):
    msg = cipher.encrypt(plaintext.encode('utf-8'))
    return msg

def decrypt(cipher, ciphertext):
    msg = cipher.decrypt(ciphertext)
    return msg.decode('utf-8')

# compute hash for messages
def computehash(key, message):
	content = f"{key}||{message}||{key}"
	temphash = hashlib.sha1(content.encode('utf-8'))
	contenthash = temphash.hexdigest()
	return contenthash

#chatroom
def sending(s, key):
	while True:
		msg = input("")
		if msg.lower().strip() == 'exit':
			print("--Program terminated due to exit--")
			s.close()
			os._exit(1)
		else:
			h = computehash(key, msg) # H(K||M||K)
			c = encrypt(createcipher(key),f"{msg}||{h}")# E(K, M||hash)
			s.send(c)
	
def receiving(s, key):
	while True:
		data = s.recv(2048)
		if not data:
			print("--Program terminated due to exit--")
			s.close()
			os._exit(1)
		
		plaintext = decrypt(createcipher(key), data)
		plaintext = plaintext.split('||')
		msg = plaintext[0]
		temphash = plaintext[1]
		result = computehash(key, msg)
		if temphash == result: # compare hash' = hash
			print("From Client: ", msg)
		else:
			print("--Program terminated due to message decryption failed--")
			s.close()
			os._exit(1)

# main program
def main():
	# read file and get their contents for Diffie Hellman Parameters
	with open("pgpw.txt", "r") as ro:
		row = ro.readline()
		rowsplit = row.split(',')
		password = rowsplit[2]
		p = rowsplit[0]
		g = rowsplit[1]

	# UDP
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(5)
	hostup = True
	print("--Host is UP, listening..--")
	DHcount = 1
	start = True
	
	# Waiting for client
	client, addr = s.accept()

	# while loop
	try:
		while True:
			name = ''
			data = client.recv(2048)
			
			if not data:
				print("--DH protocol failed as no response received from client--")
				client.close()
				sys.exit()
			
			if start:
				if data.decode('utf-8') == 'Client':
					name = 'Client'
					print(f"--Connecting to {name}--")
					client.send(b'Host')
					start = False
			
			if DHcount == 1: # DH protocol is made and adjusted based on https://www.geeksforgeeks.org/implementation-diffie-hellman-algorithm/
				print("--Starting Diffie Hellman Protocol--")
				# Host generates random a (for my case, I will be using RN generated from 10 to 100)
				a = random.randint(10,100)
				# Host should send E(H(PW), p, g, g^a mod p)
				# In my assg, I will be using Alleged RC4 (ARC4 from pycryptodome as official RC4 is not released)
				# Instead of sending E(H(PW), p, g, g^a mod p), I will send E(p, g, g^a mod p) as E encryption key is H(PW)
				hostcomputation = int(pow(int(g),a,int(p))) # g**a % p
				msgtoencrypt = f"{p},{g},{str(hostcomputation)}"
				print(f"--Initiating DH protocol with client by sending (p, g, g^a mod p): {msgtoencrypt}--")
				cipher = createcipher(password)
				ciphertext = encrypt(cipher,msgtoencrypt)
				client.send(ciphertext) # send (p, g, g^a mod p) to client
				DHcount = DHcount + 1 # go to next step of protocol
			elif DHcount == 2:
				cipher = createcipher(password)
				plaintext = decrypt(cipher, data)	
				clientcomputation = int(plaintext)
				print(f"--Received response from client: {plaintext}--")
				k = str(int(pow(clientcomputation, a, int(p)))) #shared key K
				print(f"--Shared key: {k}--")
				nonceA = random.randint(10,100)# random nonce
				cipher = createcipher(k)
				ciphertext = encrypt(cipher, str(nonceA))
				client.send(ciphertext)
				print(f"--Sending (nonceA) to client: {nonceA}--")
				DHcount = DHcount + 1
			elif DHcount == 3:
				plaintext = decrypt(createcipher(k), data)
				print(f"--Received response from client: {plaintext}--")	
				plaintext = plaintext.split(',')
				response = plaintext[0]
				nonceB = plaintext[1]
				if (int(response) == nonceA + 1): # check challenges of nonceA+1 = client's response of nonceA, if yes, send nonceB+1
					ciphertext = encrypt(createcipher(k), str(int(nonceB)+1))
					print(f"--Sending (nonceB+1) to client: {str(int(nonceB)+1)}--")	
					client.send(ciphertext)
					break
				else:
					raise Exception
					
		if hostup:
			print("--Handshake successful, you may send messages now!--")
			
		sendthread=threading.Thread(target=sending, args=[client,k])
		recvthread=threading.Thread(target=receiving, args=[client,k])

		sendthread.start()
		recvthread.start()
		
	except Exception as e:
		print("--Login failed--")
		client.close()
		sys.exit()
		
	
main()
