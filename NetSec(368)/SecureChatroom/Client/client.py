import socket
import threading
import os, sys
import random
import hashlib
from Crypto.Cipher import ARC4

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

# compute hash for H(K||M||K)
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
			print("From Host: ", msg)
		else:
			print("--Program terminated due to message decryption failed--")
			s.close()
			os._exit(1)
		
def main():
	password = input("Password>>") # get user input for password
	pw = hashlib.sha1(password.encode('utf-8'))
	pwhash = pw.hexdigest()
	host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	host.connect((HOST, PORT))
	host.send(b'Client')

	message = ''
	DHcount = 0
	start = True
	clientup = True
	try:
		while True:
			data = host.recv(2048) # receive response
			if DHcount == 1: # DH protocol is made and adjusted based on https://www.geeksforgeeks.org/implementation-diffie-hellman-algorithm/
				print("--Starting Diffie Hellman Protocol--")
				cipher = createcipher(pwhash)
				msg = decrypt(cipher, data)
				print(f"--Received response from host: {msg}--")
				msg = msg.split(',')
				p = int(msg[0])
				g = int(msg[1])
				hostcomputation = int(msg[2])
				
				b = random.randint(10,100)
				clientcomputation = int(pow(int(g),b,int(p)))	
				cipher = createcipher(pwhash)
				ciphertext = encrypt(cipher,f"{str(clientcomputation)}")
				print(f"--Sending (g^b mod p) to host: {str(clientcomputation)}--")
				host.send(ciphertext) # send (g^b mod p) to host
				k = str(int(pow(hostcomputation, b, p))) # shared key K
				print(f"--Shared key: {k}--")
				DHcount = DHcount + 1 # go to next step of protocol
			elif DHcount == 2:
				cipher = createcipher(k)
				plaintext = decrypt(cipher, data)
				print(f"--Received response from host: {plaintext}--")	
				nonceB = random.randint(10,100) # random nonce
				nonceA = int(plaintext) + 1
				
				cipher = createcipher(k) 
				ciphertext = encrypt(cipher, f"{nonceA},{str(nonceB)}")
				print(f"--Sending (nonceA+1, nonceB) to host: {nonceA},{str(nonceB)}--")
				host.send(ciphertext)
				DHcount = DHcount + 1
			elif DHcount == 3:
				plaintext = decrypt(createcipher(k),data)
				print(f"--Received response from host: {plaintext}--")				
				if (int(plaintext) == nonceB + 1):
					break
				else:
					raise Exception # fail challenge
				
			if start:
				if data.decode('utf-8') == 'Host':
					name = 'Host'
					print(f"--Connecting to {name}--")
					start = False
					DHcount = DHcount + 1

		if clientup:
			print("--Handshake successful, you may send messages now!--")
		
		sendthread=threading.Thread(target=sending, args=[host, k])
		recvthread=threading.Thread(target=receiving, args=[host, k])

		sendthread.start()
		recvthread.start()
	except UnicodeDecodeError as e:
		print("--Wrong Password, DH protocol failed--")
		host.close()
		sys.exit()
	except Exception as e:
		print("--Login failed--")
		host.close()
		sys.exit()
			
	
main()

