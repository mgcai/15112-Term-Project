#############################
# Sockets Client 
# by Rohan Varma
# adapted by Kyle Chin
# adapted by Michael Cai for a tech demo!
# adapted into a pregame lobby!
# adapted into entire run function... :/ (for now hopefully)
# wind doesnt work as intended, friction happens
# lightning hit box very poor
# random platforms are not entirely working, see generate level example to see it generated.
#############################

import socket
import threading
from queue import Queue

HOST = "128.237.117.142"# put your IP address here if playing on multiple computers
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
# keyreleased added into run function
# timerfired wrapper function edited

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
from weather import weather
from Platforms import Platform
from tkinter import *
import string
import mapGen

####################################
# customize these functions
####################################

def init(data):
    #Lobby init
    data.me = User("Me")
    data.nameChange = ""
    data.otherStrangers = dict()
    data.isLobby = True
    data.isPlaying = False
    
    #scrolling
    data.scrollMargin = 30
    data.scrollX = 0
    data.scrollY = 0
    
    #platforms (will be randomly generated)
    data.testPlatform = Platform(data.width-(2*data.scrollMargin),data.height-30,40)
    data.bottomPlatform = Platform(0,data.height-5,data.width*3)
    data.p1 = Platform(data.width-(3*data.scrollMargin),data.height-60,40)
    data.p2 = Platform(data.width-(4*data.scrollMargin),data.height-80,40)
    data.p3 = Platform(data.width+(3*data.scrollMargin),data.height-60,40)
    data.p4 = Platform(data.width+(4*data.scrollMargin),data.height-80,40)
    data.platforms = [data.testPlatform,data.bottomPlatform,data.p1,data.p2,data.p3,data.p4]    

    #Runner init
    data.player = Player(data.scrollMargin,data.height-10)
    data.isJumping = False
    data.isAcceleratingRight = False
    data.isAcceleratingLeft = False
    data.isFalling = False
    data.canMove = True
    data.currentPlatform = data.bottomPlatform
    data.stunCount = 0
    
    #God init
    data.gameWeather = weather(0)
    data.canRain = True
    data.canLightning = True
    data.willLightning = False
    data.isLightning = False
    data.lightning = None
    data.lightningEnd = data.height
    data.lightningCounter = 0

def mousePressed(event, data):
    msg = ""
    #lobby role choice and ready
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
    
    #lightning strikes for God
    if data.isPlaying and data.me.role == "God":
        if data.canLightning:
            data.canLightning = False
            data.willLightning = True
            data.lightning = event.x
        for platform in data.platforms:
            if data.lightning > platform.x and \
            data.lightning < platform.x+platform.length:
                y = platform.y
                if y < data.lightningEnd:
                    data.lightningEnd = y
    # sends the message to other players
    if (msg != ""):
        print ("sending: ", msg,)
        data.server.send(msg.encode())
        
def keyPressed(event, data):
    msg = ""
    #lobby name change
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
            
    #movement controls (runner)
    if data.isPlaying and data.me.role == "Runner":
        if event.keysym == "Left":
            data.isAcceleratingLeft = True
            
        elif event.keysym == "Right":
            data.isAcceleratingRight = True

        elif event.keysym == "Up":
            data.isJumping = True
            
    #wind control (God)
    if data.isPlaying and data.me.role == "God":
        if event.keysym == "Left":
            data.gameWeather.wind -= 1
            if data.gameWeather.wind < -10:
                data.gameWeather.wind = -10
            msg = "changeWind %d\n" %data.gameWeather.wind
        elif event.keysym == "Right":
            data.gameWeather.wind += 1
            if data.gameWeather.wind > 10:
                data.gameWeather.wind = 10
            msg = "changeWind %d\n" %data.gameWeather.wind
            
    # sends the message to other players
    if (msg != ""):
        print ("sending: ", msg,)
        data.server.send(msg.encode())
        
def keyReleased(event,data):
    #runner backend controls
    if data.isPlaying and data.me.role == "Runner":
        if event.keysym == "Left":
            data.isAcceleratingLeft = False
        if event.keysym == "Right":
            data.isAcceleratingRight = False

#runner landing function
def landing(data, player, platform):
    (x,y) = player.getCoords()
    (pX,pY) = platform.getCoords()
    length = platform.getLength()
    if x >= pX and x <= pX + length:
        if player.canLand() and player.lastY() <= pY and y >= pY:
            player.placePlayerY(pY-5)
            data.isJumping = False
            data.isFalling = False
            player.resetJump()
            data.currentPlatform = platform
    
#sends the location of the runner(called inside timerFiredWrapper)
def sendLocation(data):
    (x,y) = data.player.getCoords()
    msg = "playerCoords %d %d %d %d\n" %(x,y,data.scrollX,data.scrollY)
    #prints too much lmao
    #print ("sending: ", msg,)
    data.server.send(msg.encode())

#timerFired for the runner
def timerFiredRunner(data):
    
    hitByLightning(data)
    
    if data.canMove == False:
        data.stunCount += 1
        if data.stunCount == 100:
            data.stunCount = 0
            data.canMove = True
        
    if data.isJumping:
        data.player.jump()
        for platform in data.platforms:
            landing(data,data.player,platform)
            
    if data.isFalling:
        data.player.fall()
        for platform in data.platforms:
            landing(data,data.player,platform)
        
    if data.isAcceleratingRight:
        data.player.accelerate('right')
        
    if data.isAcceleratingLeft:
        data.player.accelerate('left')
    
    if not (data.isAcceleratingLeft or data.isAcceleratingRight):
        data.player.moveFriction()
    
    if data.canMove:
        data.player.move()
        
    if (data.player.x < data.scrollX + data.scrollMargin):
        data.scrollX = data.player.x - data.scrollMargin
    if (data.player.x > data.scrollX + data.width - data.scrollMargin):
        data.scrollX = data.player.x - data.width + data.scrollMargin
    data.scrollY = data.height - data.player.y - 50

    if data.currentPlatform == None:
        data.player.fall()
        data.isJumping = True
    
    else:
        platform = data.currentPlatform
        (x,y) = data.player.getCoords()
        (pX,pY) = platform.getCoords()
        length = platform.getLength()
        if x <= pX or x >= pX + length:
            data.isFalling = True

#times lightning and sends msg for when lightning is present
def lightningTimer(data):
    msg = ""
    if data.willLightning == True:
        data.lightningCounter += 1
        msg = "willLightning %d\n" %data.lightning
    if data.lightningCounter == 5:
        data.isLightning = True
        msg = "lightningCreate %d %d\n" %(data.lightning,data.lightningEnd)
    if data.lightningCounter == 20:
        data.isLightning = False
        msg = "lightningPop donzo\n"
    if data.lightningCounter == 40:
        data.lightningCounter = 0
        data.canLightning = True
        data.willLightning = False
        data.lightning = None

    if (msg != ""):
        print ("sending: ", msg,)
        data.server.send(msg.encode())
    
def startGame(data):
    for player in data.otherStrangers:
        if data.otherStrangers[player].ready and data.me.ready:
            data.isLobby = False
            data.isPlaying = True
                
#main timerFired for receiving msgs
def timerFired(data):

    # timerFired receives instructions and executes them
    while (serverMsg.qsize() > 0):
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
        
        elif command == "playerCoords":
            x = int(msg[2])
            y = int(msg[3])
            sX = int(msg[4])
            sY = int(msg[5])
            data.player.x = x
            data.player.y = y
            data.scrollX = sX
            data.scrollY = sY
        
        elif command == "willLightning":
            data.willLightning = True
            data.lightning = int(msg[2])
            
        elif command == "lightningCreate":
            data.lightning = int(msg[2])
            data.lightningEnd = int(msg[3])
            data.isLightning = True
            
        elif command == "lightningPop":
            data.lightning = None
            data.isLightning = False
            data.willLightning = False
            
        elif command == "changeWind":
            windSpeed = int(msg[2])
            data.player.velocity += windSpeed

            
        serverMsg.task_done()
        
def hitByLightning(data):
    sX = data.scrollX 
    sY = data.scrollY
    if data.isLightning:
        if data.player.x>=data.lightning-2 and data.player.x<=data.lightning+2:
            if data.player.y < data.lightningEnd+sY:
                data.canMove = False


def redrawAll(canvas, data):
    # lobby drawing
    if data.isLobby:
        #role selection
        canvas.create_rectangle(0,data.height/2,data.width/2,data.height,
                                fill="blue")
        canvas.create_rectangle(data.width/2,data.height/2,data.width,
                                data.height, fill="red")
        canvas.create_text(data.width*(3/4),data.height*(3/4), 
                           text = "Click to be the Runner!",font="Helvetica 12")
        canvas.create_text(data.width*(1/4),data.height*(3/4),
                           text = "Click to be God!", font="Helvetica 12")
        #ready button
        if data.me.ready == True:
            color = "green"
        else: 
            color = "yellow"
        canvas.create_rectangle(0,data.height/2-50,data.width,data.height/2,
                                fill=color)
        canvas.create_text(data.width/2,data.height/2-25, text="ready?")
        # other player
        canvas.create_text(data.width/2, 10,text="type anywhere to change name")
        canvas.create_text(10,70,text="Other Player:", font="Helvetica 12", 
                            anchor = NW)
        for item in (data.otherStrangers):
            canvas.create_text(10,90,text = str(data.otherStrangers[item])+
                            " playing as: " + data.otherStrangers[item].role, 
                            font="Helvetica 12", anchor = NW)
        # me
        name = str(data.me)
        canvas.create_text(10,30,text="My name is: "+ name + " playing as: " + 
                            data.me.role, font="Helvetica 12",anchor = NW)
        canvas.create_text(10,50,text="Changing name to: " + data.nameChange,
                            font="Helvetica 12", anchor = NW)
                            
    #playing drawing
    if data.isPlaying:
        (x,y) = data.player.getCoords()
        sX = data.scrollX 
        sY = data.scrollY
        canvas.create_oval(x-5-sX,y-5+sY,x+5-sX,y+5+sY,fill="blue")
        for platform in data.platforms:
            (x,y) = platform.getCoords()
            length = platform.getLength()
            canvas.create_rectangle(x-sX,y+sY,x+length-sX,y+2+sY,fill="black")
            
        """
        if data.willLightning and data.lightning != None:
            canvas.create_rectangle(data.lightning-10-sX,-sY,data.lightning+10-sX,
                                    5-sY,fill="gray")
        """
        if data.isLightning:
            canvas.create_rectangle(data.lightning-2,0,data.lightning+2,
                                    data.lightningEnd+sY,fill="yellow")
                        
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
        startGame(data)
        if data.me.role == "Runner":
            timerFiredRunner(data)
            sendLocation(data)
        if data.me.role == "God":
            lightningTimer(data)
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
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    root.bind("<KeyRelease>", lambda event:
                            keyReleaseWrapper(event,canvas,data))

    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

run(400, 400, serverMsg, server)