import os
import random
import hashlib
import json

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-5ad314dd-b245-41dd-9a06-d14031293e0f'
pnconfig.publish_key = 'pub-c-8e59030e-2c9d-471f-9bf9-d8ff221dfa0d'
pnconfig.user_id = "alice"
pubnub = PubNub(pnconfig)

# for tic tac toe
board = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "G": 0, "H": 0, "I": 0}      
count = 0

def generateBlock(position):
	global count
	nonce = 0
	cond = True
	count = count + 1
	fr = open(f'alice/block{count-1}.json', "r")
	preblk = fr.read()
	fr.close()
	hashValue = hashlib.sha256(preblk.encode()).hexdigest()
	
	while(cond):
		block = json.dumps({'Block number': count, 'Hash': hashValue, 'Nonce': nonce, 'Transaction': ["Alice", position]}, sort_keys=False,indent=4, separators=(',', ': '))
		hashnonce = hashlib.sha256(block.encode()).hexdigest()
		if int(hashnonce[0:4],16) < 2^244:
			cond = False
		nonce = nonce + 1
		
	fr = open(f'alice/block{count}.json', "w")
	fr.write(block)
	fr.close()
	
	return block

def generateRandomBlockList():
	boardlist = []
	for key,value in board.items():
		if value == 1:
			pass
		else:
			boardlist.append(key) # append non-selected space in board
	return boardlist

def selectRandomPlacement(tempboard):
	tempchoice = random.choice(tempboard) # random space
	board[tempchoice] = 1
	print("----------------------------------------\nTic Tac Toe: ", board, "\n----------------------------------------")
	return tempchoice

def writeBlock(block):
	formatblock = json.loads(block)
	result = compareBlock(formatblock)
	if(result):
		fw = open(f'alice/block{count}.json',"w")
		fw.write(block)
		fw.close()
		return formatblock
	else:
		return False

def confirmPlacement(block):
	temp = block["Transaction"]
	placement = temp[1]
	board[placement] = 1
	print("----------------------------------------\nTic Tac Toe: ", board, "\n----------------------------------------")
	
def compareBlock(block):
	_hashvalue = block["Hash"]
	fr = open(f'alice/block{count-1}.json', "r")
	preblk = fr.read()
	fr.close()
	hashvalue = hashlib.sha256(preblk.encode()).hexdigest()
	if _hashvalue == hashvalue:
		print(f"----------------------------------------\n--Block Validation Process--\nHashes comparison between block{count-1} and block{count}: True\n----------------------------------------")
		return True
	else:
		print(f"----------------------------------------\n--Block Validation Process--\nHashes comparison between block{count-1} and block{count}: False\n----------------------------------------")
		return False

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];

class MySubscribeCallback(SubscribeCallback):
	def presence(self, pubnub, presence):
		pass

	def status(self, pubnub, status):
		if status.category == PNStatusCategory.PNConnectedCategory:
			# Connect event. You can do stuff like publish, and know you'll get it.
			# Or just use the connected event to confirm you are subscribed for
			# UI / internal notifications, etc
			print("----------------------------------------\nTic Tac Toe: ", board, "\n----------------------------------------")
			greeting = {"sender": "Alice", "message": "Hello from Alice", "turn": 0} # To check response of first player
			pubnub.publish().channel('Channel-x5wtpz6e1').message(greeting).pn_async(my_publish_callback)
	def message(self, pubnub, message):
		# Handle new message stored in message.message
		tempmessage = message.message
		global count
		# Verify and validate message incoming first
		if tempmessage["sender"] == "Bob" and tempmessage["turn"] == 0: # If Alice is first player, Alice will generate first block only after Bob sent his first message and vice versa
			print(tempmessage["message"])
			_templist = generateRandomBlockList()
			placement =  selectRandomPlacement(_templist)
			tempblock = generateBlock(placement)
			messagetosend = {"sender": "Alice", "message": tempblock, "turn": count}
			pubnub.publish().channel('Channel-x5wtpz6e1').message(messagetosend).pn_async(my_publish_callback)
			print(f'Block {count} generated and sent')
		elif tempmessage["sender"] == "Bob" and 9 > tempmessage["turn"] > 0:
			tempblock = tempmessage["message"]
			count = tempmessage["turn"]
			tempblock = writeBlock(tempblock)
			if tempblock != False:	
				confirmPlacement(tempblock)
				print(f'Block {count} received from Bob validated and recorded successfully')
				templist = generateRandomBlockList()
				placement = selectRandomPlacement(templist)
				tempblock = generateBlock(placement)
				messagetosend = {"sender": "Alice", "message": tempblock, "turn": count}
				pubnub.publish().channel('Channel-x5wtpz6e1').message(messagetosend).pn_async(my_publish_callback)
				print(f'Block {count} generated and sent')
			else:
				print("Validation of block received failed, Please restart again")
		elif tempmessage["sender"] == "Bob" and  tempmessage["turn"] == 9:
			tempblock = tempmessage["message"]
			count = tempmessage["turn"]
			tempblock = writeBlock(tempblock)
			if tempblock != False:
				confirmPlacement(tempblock)
				print(f'Block {count} received from Bob validated and recorded successfully')
			else:
				print("Validation of block received failed, Please restart again")
			
		if count >= 9:
			pubnub.unsubscribe_all()
			print("----------------------------------------\nFinal Tic Tac Toe: ", board, "\n----------------------------------------")
			os._exit(0)

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('Channel-x5wtpz6e1').execute()
