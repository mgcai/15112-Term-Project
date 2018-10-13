#############################
# Sockets Server Demo
# by Rohan Varma
# adapted by Kyle Chin
# adapted by Michael Cai!
#############################

import socket
import pickle
import threading
from queue import Queue

HOST = "128.237.113.109" # put your IP address here if playing on multiple computers
PORT = 50003
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("looking for connection")

def handleClient(client, serverChannel, cID, clientele):
  client.setblocking(1)
  msg = ""
  while True:
    try:
      msg += pickle.loads(client.recv(10))
      command = msg.split("\n")
      while (len(command) > 1):
        readyMsg = command[0]
        msg = "\n".join(command[1:])
        serverChannel.put(str(cID) + " " + readyMsg)
        command = msg.split("\n")
    except:
      # we failed
      return

def serverThread(clientele, serverChannel):
  while True:
    msg = serverChannel.get(True, None)
    print("msg recv: ", msg)
    msgList = msg.split(" ")
    senderID = msgList[0]
    instruction = msgList[1]
    details = " ".join(msgList[2:])
    if (details != ""):
      for cID in clientele:
        if cID != senderID:
          sendMsg = instruction + " " + senderID + " " + details + "\n"
          clientele[cID].send(pickle.dumps(sendMsg))
          print("> sent to %s:" % cID, sendMsg[:-1])
    print()
    serverChannel.task_done()

clientele = dict()
playerNum = 0

serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()

names = ["Player1", "Player2", "Player3", "Player4"]

while True:
  client, address = server.accept()
  # myID is the key to the client in the clientele dictionary
  myID = names[playerNum]
  print(myID, playerNum)
  for cID in clientele:
    print (repr(cID), repr(playerNum))
    clientele[cID].send(pickle.dumps("newPlayer %s\n" % myID))
    client.send(pickle.dumps("newPlayer %s\n" % cID))
  clientele[myID] = client
  client.send(pickle.dumps("myIDis %s \n" % myID))
  print("connection recieved from %s" % myID)
  threading.Thread(target = handleClient, args = 
                        (client ,serverChannel, myID, clientele)).start()
  playerNum += 1