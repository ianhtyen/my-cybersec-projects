Name: Hong Ter Yen
Python version used: 3.10.5
Program that I tested on: Linux

List of python libraries that I imported for this program
-socket
-threading
-os
-sys
-random
-hashlib
-ARC4 (Crypto.Cipher) (pycryptodome)
-number (Crypto.Util) (pycryptodome)

To make sure you did not miss any modules when compiling, please install:
- by 'pip install -r requirements.txt'

To run the program,
-Go to 'Host' directory, run 'python generatefile.py' first to generate the text file for p,g and passwordhash (password is hardcoded and was assumed to be known between the two parties (the password used is alicebob, you can change it to other preferred password))
- run 'python host.py'
- run 'python client.py'

That's it. You should be able to send and receive messages after "--Handshake successful, you may send messages now!--" is printed on the terminals.
