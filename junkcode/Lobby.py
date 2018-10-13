#############################
# Sockets Client 
# by Rohan Varma
# adapted by Kyle Chin
# adapted by Michael Cai for a tech demo!
# adapted into a pregame lobby!
#############################

import socket
import threading
from queue import Queue

HOST = "128.237.198.180"
 # put your IP address here if playing on multiple computers
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

# events-example0.py from 15-112 website
# Barebones timer, mouse, and keyboard events

##########################
# User Class
##########################

class User(object):

    def __init__(self, PID):
        self.PID = PID
        self.role = "No Role!"
        self.ready = False
        
    def __repr__(self):
        return self.PID

    def changePID(self, PID):
        self.PID = PID

    def chooseRole(self,role):
        self.role = role
    
    def getReady(self):
        self.ready = not self.ready

####################################
#imports
####################################

from Player import Player
from Platforms import Platform
from tkinter import *
import random
import string
import runPlayer

####################################
# customize these functions
####################################

def init(data):
    data.me = User("Me")
    data.nameChange = ""
    data.otherStrangers = dict()
    data.isLobby = True
    data.isPlaying = False

def mousePressed(event, data):
    msg = ""
    if data.isLobby:
        if not data.me.ready:
            if event.x < data.width/2 and event.y > data.height/2:
                for player in data.otherStrangers:
                    if data.otherStrangers[player].role != "God":
                        data.me.chooseRole("God")
                        msg = "playerRole God\n"
                
            if event.x > data.width/2 and event.y > data.height/2:
                for player in data.otherStrangers:
                    if data.otherStrangers[player].role != "Runner":
                        data.me.chooseRole("Runner")
                        msg = "playerRole Runner\n"       
                 
        if event.y > data.height/2 - 50 and event.y < data.height/2:
            if data.me.role != "No Role!":
                data.me.getReady()
                msg = "playerReady ready\n"
        
    elif data.isPlaying:
        if data.me.role == "Runner":
            runPlayer.mousePressed(event, data)
        elif data.me.role == "God":
            pass 
            
    if (msg != ""):
        print ("sending: ", msg,)
        data.server.send(msg.encode())
        
def keyPressed(event, data):
    msg = ""
    if data.isLobby:
        # changing name
        if event.keysym in string.ascii_letters:
            data.nameChange += event.keysym
            # update message to send
    
        elif event.keysym == "Return":
            data.me.changePID(data.nameChange)
            msg = "playerChangedName %s\n" %data.nameChange
            data.nameChange = ""
        
        elif event.keysym == "BackSpace":
            data.nameChange = data.nameChange[:-1]
            
    if data.isPlaying and data.me.role == "Runner":
        runPlayer.keyPressed(event,data)
        
        
    # send the message to other players!
    if (msg != ""):
        print ("sending: ", msg,)
        data.server.send(msg.encode())
        
def keyReleased(event,data):
    if data.isPlaying and data.me.role == "Runner":
        runPlayer.keyReleased(event,data)
        print(event.keysym)

def timerFired(data):
    
    for player in data.otherStrangers:
        # print(data.otherStrangers[player].ready) 
        if data.otherStrangers[player].ready and data.me.ready:
            data.isLobby = False
            data.isPlaying = True
            runPlayer.init(data)
            
    if data.isPlaying:
        runPlayer.timerFired(data)
    
    # timerFired receives instructions and executes them
    while (serverMsg.qsize() > 0):
        #Should use try and except here but taken out to debug
        msg = serverMsg.get(False)
        print("received: ", msg, "\n")
        msg = msg.split()
        command = msg[0]

        if (command == "myIDis"):
            myPID = msg[1]
            data.me.changePID(myPID)

        elif (command == "newPlayer"):
            newPID = msg[1]
            data.otherStrangers[newPID] = User(newPID)

        elif (command == "playerChangedName"):
            PID = msg[1]
            newPID = msg[2]
            data.otherStrangers[PID].changePID(newPID)
        
        elif (command == "playerRole"):
            PID = msg[1]
            role = msg[2]
            data.otherStrangers[PID].chooseRole(role)
            
        elif command == "playerReady":
            PID = msg[1]
            data.otherStrangers[PID].getReady()
        
        elif command == "playerLocated":
            PID = msg[1]
            x = msg[2]
            y = msg[3]
            data.otherStrangers[PID].x = x
            data.otherStrangers[PID].y = y
            
        serverMsg.task_done()

def redrawAll(canvas, data):
    if data.isLobby:
        canvas.create_rectangle(0,data.height/2,data.width/2,data.height,
                                fill="blue")
        canvas.create_rectangle(data.width/2,data.height/2,data.width,data.height,
                                fill="red")
        canvas.create_text(data.width*(3/4),data.height*(3/4), 
                            text = "Click to be the Runner!", font="Helvetica 12")
        canvas.create_text(data.width*(1/4),data.height*(3/4),
                            text = "Click to be God!", font="Helvetica 12")
        if data.me.ready == True:
            color = "green"
        else: 
            color = "yellow"
        canvas.create_rectangle(0,data.height/2-50,data.width,data.height/2,
                                fill=color)
        canvas.create_text(data.width/2,data.height/2-25, text="ready?")
        # draw other player
        canvas.create_text(data.width/2, 10, text="type anywhere to change name")
        canvas.create_text(10,70,text="Other Player:", font="Helvetica 12", 
                            anchor = NW)
        for item in (data.otherStrangers):
            canvas.create_text(10,90,text = str(data.otherStrangers[item])+
                            " playing as: " + data.otherStrangers[item].role, 
                            font="Helvetica 12", anchor = NW)
        # draw me
        name = str(data.me)
        canvas.create_text(10,30,text="My name is: "+ name + " playing as: " + 
                            data.me.role, font="Helvetica 12",anchor = NW)
        canvas.create_text(10,50,text="Changing name to: " + data.nameChange,
                            font="Helvetica 12", anchor = NW)
    if data.isPlaying:
        runPlayer.redrawAll(canvas,data)
    
                        
####################################
# use the run function as-is
####################################

def run(width, height, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)
        
    def keyReleaseWrapper(event, canvas, data):
        keyReleased(event, data)
        redrawAllWrapper(canvas,data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.server = server
    data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    if data.isLobby:
        root.bind("<Button-1>", lambda event:
                                mousePressedWrapper(event, canvas, data))
        root.bind("<Key>", lambda event:
                                keyPressedWrapper(event, canvas, data))
        root.bind("<KeyRelease>", lambda event:
                                keyReleaseWrapper(event,canvas,data))
    if data.isPlaying and data.me.role == "Runner":
        root.bind("<Button-1>", lambda event:
                                runPlayer.mousePressedWrapper(event, canvas, data))
        root.bind("<Key>", lambda event:
                                runPlayer.keyPressedWrapper(event, canvas, data))
        root.bind("<KeyRelease>", lambda event:
                                runPlayer.keyReleaseWrapper(event,canvas,data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

run(400, 400, serverMsg, server)