#!/usr/bin/env python3
import glob, subprocess
from subprocess import Popen

ALL_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	
#deSub Cipher
def decryptFile(contents, dKey):
	decrypted = ""
	tempA = dKey
	tempB = ALL_LETTERS
	
	for tempChar in contents:
		if tempChar.upper() in tempA:
			charIndex = tempA.find(tempChar.upper())
			if tempChar.isupper():
				decrypted += tempB[charIndex].upper()
			else:
				decrypted += tempB[charIndex].lower()
		else:
			decrypted += tempChar
	return decrypted
	
#txt dec
def txtDecrypt(key):
	found = False
	for item in glob.glob("*.enc"):
		decContents = ""
		fileIn = open(item,'r')
		for line in fileIn:
			decContents += decryptFile(line, key)
		fileIn.close()
		fileOut = open(item,'w')
		fileOut.writelines(decContents)
		fileOut.close()
		itemDec = item.replace("enc", "txt")
		p1 = Popen(["mv",item, itemDec])
		found = True
	return found

#write key.txt
def getKey():
	file_out = open("key.txt","r")
	return file_out.read()
	
#Start
dKey = getKey()
if txtDecrypt(dKey):
	print("decrypt success")
