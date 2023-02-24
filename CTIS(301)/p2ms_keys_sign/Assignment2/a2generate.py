#!/usr/bin/env python3
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import binascii
import random

# Number of public keys
N = 4
# Number of signatures
M = 2
# Prepare signList
signList = ["dummy"] # first dummy value in a list

# Sign message
def writeSignature(count):
	filein = open(f"scriptSig{count}.txt", "w")
	for line in signList: # write to file
		filein.write(f'{line}\n')
	filein.close()
	return True
	
def signMessage(key):
	hash_obj = SHA256.new(b"CSCI301 Contemporary topic in security")
	signer = DSS.new(key, 'fips-186-3')
	signature = signer.sign(hash_obj)
	signature_hex = binascii.hexlify(signature)
	signList.append(signature_hex) # push signed messages
    	
# Generate Key
def generateKey(count):
	pubKeyList = []
	pubKeyList.append(M) # push OP signature first
	temp = 0
	for i in range(N): # push public keys
		key = DSA.generate(2048)	
		randomTemp = random.randint(i,3)
		if temp < 2 and randomTemp == i: #randomly choose PK to sign (in order)
			signMessage(key)
			temp = temp + 1
		elif temp < 2 and i >= 2: #if theres no match and already have left at least 2 PK in order, sign
			if temp == 1 and randomTemp != i:
				pass
			else:
				signMessage(key)
				temp = temp + 1
		publicKey = binascii.hexlify(key.publickey().export_key())
		pubKeyList.append(publicKey)
	pubKeyList.append(N) # push number of PKs
	#print(len(pubKeyList))
	filein = open(f"scriptPubKey{count}.txt", "w")
	for line in pubKeyList: # write to file
		filein.write(f'{line}\n')
	filein.close()
	return True

for i in range(1,4):
	if len(signList) != 0:
		signList.clear()
		signList.append("dummy") # push dummy value first
	if generateKey(i) and writeSignature(i):
		print(f"Successfully generated no{i} file")

