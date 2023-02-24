#!/usr/bin/env python3
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import binascii

stack = []
pKeyList = []
signList = []
hash_obj = SHA256.new(b"CSCI301 Contemporary topic in security")

# Script construction
def scriptSig(input):
	fileout = open(f"scriptSig{input}.txt", "r")
	print(f"Processing scriptSig{input} into stack")
	print("--------------------------")	
	for line in fileout:
		stack.append(line.rstrip('\n'))
	fileout.close()
	print("Done")
	print("--------------------------\n")	
		
def scriptPubKey(input):
	fileout = open(f"scriptPubKey{input}.txt", "r")
	print(f"Processing scriptPubKey{input} into stack")
	print("--------------------------")	
	for line in fileout:
		stack.append(line.rstrip('\n'))
	fileout.close()
	print("Done")
	print("--------------------------\n")		

# Script execution
def checkMultiSig():
	count = 0
	noInput = input("Number of script file to be used:")
	print("--------------------------\n")
	scriptSig(noInput) # construct script 1
	scriptPubKey(noInput) # construct script 2
	print("|Stack info after construct|")
	print("-------------")
	print(stack)
	print("-------------")
	print(f"Size of stack: {len(stack)}")
	print("--------------------------\n")
	if len(stack) != 0:
		print("Popping Numbers of Public Keys")
		print("--------------------------\n")	
		N = stack.pop() # number of pkeys
		print(f"Done (Number of Public Keys: {N})")
		print("--------------------------\n")	
		for i in range(int(N)):
			pKeyList.append(stack.pop())
		if len(pKeyList) == int(N):
			print("All PKeys are popped from stack into pKeyList")
			print("--------------------------\n")	
		print("Popping numbers of signatures")
		print("--------------------------\n")	
		M = stack.pop() # number of signatures
		print(f"Done (Number of Signature: {M})")
		print("--------------------------\n")	
		for i in range(int(M)):
			signList.append(stack.pop())
		if len(signList) == int(M):
			print("Signatures are popped from stack into signList")
			print("--------------------------\n")
	# stack information update
	print("|Stack info|")
	print("-------------")
	print(stack)
	print("-------------")
	print(f"Size of stack: {len(stack)}")
	print("--------------------------\n")
	print("|pKeyList|")
	print("-------------")
	print(pKeyList)
	print("--------------------------\n")
	print("|signList|")
	print("-------------")
	print(signList)
	print("--------------------------\n")
	tempCount = int(N)
	print("-------------")
	print("|Signature Verification Info|")
	print("-------------\n")
	while len(signList) > 0:
		temp = signList.pop()[2:-1].encode("utf-8")
		signature = binascii.unhexlify(temp)
		while len(pKeyList) > 0:
			temp1 = pKeyList.pop()[2:-1].encode("utf-8")
			publicKey =  DSA.import_key(binascii.unhexlify(temp1))
			verifier = DSS.new(publicKey, 'fips-186-3')
			try:
				verifier.verify(hash_obj, signature)
				print(f"Signature {count + 1} verified")
				print("--------------------------\n")
				count = count + 1
				break
				
			except ValueError:
				print(f"Signature {count+1} unable to be verified")
				print("--------------------------\n")
	if count == int(M):
		stack.clear()
		stack.append(1) # p2ms style from learnabitcoin, 1 as true
		print("|Stack info|")
		print("-------------")
		print(stack)
		print("--------------------------\n")
	else:
		stack.clear()
		stack.append(0) # 0 as false
		print("|Stack info|")
		print("-------------")
		print(stack)
		print("--------------------------\n")
	
	return stack
		
check = checkMultiSig()
if check[0] == 1:
	print("P2MS successful")
else:
	print("P2MS failed")

