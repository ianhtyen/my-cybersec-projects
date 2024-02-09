#!/usr/bin/env python3
import hashlib
import time
import sys

# main (for rainbow table)
def main():
    file_target = sys.argv[1]
    start = time.time()
    rainbowlist = []
    passwordlist = []
    # Read in the Passwords.txt
    with open(file_target) as file:
        passwordlist = [line.rstrip() for line in file]
    # Report on number of words read in
    password_size = len(passwordlist)
    print(f'### {password_size} words has been retrieved ###')
    # Computation start (First step of Q2)
    check = True
    print('### Process has started, Please wait... ###')
    while(check):
        # get the first or next unused words
        selectedpass = passwordlist[0]
        passwordlist.remove(selectedpass) # remove used words from unused word list
        hash = hash_password(selectedpass)
        reduction = reduction_function(hash, password_size)
        lasthash = ""
        # end of unused words
        if len(passwordlist) < 1:
            check = False
        # create chain
        for _ in range(4):
            temp = get_password(reduction, file_target)
            if (temp in passwordlist): # if used words are in list, remove from unused word list
                passwordlist.remove(temp)
            temphash = hash_password(temp)
            reduction = reduction_function(temphash, password_size) 
            lasthash = temphash
        # rainbow table construction
        rainbowresult = f'{lasthash}|{selectedpass}' # first step of Q2(d) 
        rainbowlist.append(rainbowresult + "\n") # entry of rainbow table list
    write_password(rainbowlist) # Q3 and Q4
    end = time.time()
    print(f"### Time taken for the construction of rainbow table: {end-start} ###")

    # hash input (second step)
    while True:
        hashvalue = hash_input()
        result = check_hash(hashvalue,password_size,file_target)
        # Result
        if len(result) == 0:
            print("### Invalid hash value in Rainbow Table ###")
            pass
        else:
            result_image = crack_hash(result, hashvalue, password_size)
            print(f"### Original Value of the Hash Input: {result_image} ({hashvalue}) ###")
    
# reduction function
def reduction_function(hash, size):
    # hash modulo size of password file
    hash = "0x" + hash
    r = (int(hash,16) % size)
    return r

def hash_password(password):
    return hashlib.md5(password.encode('utf8')).hexdigest()

def get_password(number, file_name):
    with open(file_name) as file:
        for count, line in enumerate(file):
            if count == number:
                return line.rstrip()

def write_password(rainbowtable):
    with open("Rainbow.txt", "w") as file:
        rainbowtable.sort()
        print(f'### Number of lines in Rainbow Table: {len(rainbowtable)} ###')
        file.writelines(rainbowtable)

# crack hash (rainbow attack)
def hash_input():
    while True:
        hash_value = input('Input your hash value: ')
        if len(hash_value) == 32:
            return hash_value
        elif hash_value == "quit":
            return sys.exit(0)
        else:
            print("### Hash value can only be 32 characters long ###")

def check_hash(hash, size, file):
    hashlist = check_table(hash)
    if len(hashlist) > 0:
        return hashlist
    else:
        count = 0
        while True:
            print("### Reduction in process ###")
            temp_reduction = reduction_function(hash, size)
            temp_pass = get_password(temp_reduction,file)
            temp_hash = hash_password(temp_pass)
            temp_list = check_table(temp_hash)
            if len(temp_list) == 0: # cant find, reduce again
                count = count + 1
                hash = temp_hash
            elif count > 20: #stop finding hash if cannot find
                print()
                return []
            else:
                return temp_list

def check_table(hash):
    hashlist = []
    with open('Rainbow.txt', 'r') as file:
        temp = ""
        found = False
        for line_no, line in enumerate(file):
            if hash in line: # found
                temp = line.rstrip().split('|')
                hashlist.append(line.rstrip())
                print(f"### Found on line {line_no + 1} for hash '{temp[0]} ({temp[1]})' ###")  
                found = True
            if found and temp[0] not in line:
                print(f"### Hash check in rainbow table has ended on line {line_no + 1} ###")
                break
    if found:
        return hashlist
    else:
        print("### Not found ###")
        return hashlist
                    
def crack_hash(rainbowlist, hashinput, size):
    for item in rainbowlist:
        itemlist = item.split('|')
        pre_image = itemlist[1]
        print(f"### Using '{itemlist[1]}' to crack hash ###")
        for i in range(5):
            temp = hash_password(pre_image)
            if temp == hashinput:
                return pre_image
            else:
                print(f"Reduction Count: {i}")
                reduce = reduction_function(temp, size)
                pre_image = get_password(reduce, "Passwords.txt")
    return "Unable to get pre-image for"

main()