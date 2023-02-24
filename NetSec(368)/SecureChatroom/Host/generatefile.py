import hashlib
from Crypto.Util import number

# generate file
def generatetextfile():
    # Password (share common password which is alicebob)
    pw = hashlib.sha1(b'alicebob')
    pwhash = pw.hexdigest()
    p, g = generatepg()

    with open("pgpw.txt", "w") as wo:
        row = f"{str(p)},{str(g)},{pwhash}"
        wo.write(row)

# generate p and g = 2 (universal primitive root modulo) I will be using 512 bits
def generatepg():
    p = number.getPrime(512)
    return p, 2
    
generatetextfile()
