#############################
# Michael Cai; user client
# Kyle's dots example used as starter code, thanks kyle!

#############################

import socket
import threading
from queue import Queue

HOST = "128.237.99.5" # put your IP address here if playing on multiple computers
PORT = 50007

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
      
# used events-example0.py from 15-112 website as starter code!
# tkinter is frontend module
# added keyReleased to run function, edited wrapper functions in run function
####################################
from tkinter import *
import random
import string
import math
from Player import Player
from bullet import Bullet
from Platforms import Platform
from mapGen import generatePlatform
from PIL import ImageGrab, ImageTk, Image

####################################
# customize these functions
####################################

def init(data):
    #player
    data.scrollMargin = 30
    data.me = Player("Player1",data.width-data.scrollMargin,data.height-200)
    data.isJumping = False
    data.isAcceleratingRight = False
    data.isAcceleratingLeft = False
    data.isFalling = False
    data.start = False
    data.myBullet = None
    data.fired = False
    data.canFire = True
    data.fireCount = 0
    data.isPlaying = False
    data.isLobby = True
    data.isDeadSplash = False
    data.instructions = False
    data.nameChange = ""
    data.score = data.me.score + data.height - 200

    #platforms
    data.testPlatform = Platform(data.width-(2*data.scrollMargin),data.height-250,40)
    data.bottomPlatform = Platform(data.width-(2*data.scrollMargin),data.height-205,40)
    data.platforms = [data.bottomPlatform,data.testPlatform]
    data.currentPlatform = data.bottomPlatform
    
    #other people
    data.otherStrangers = dict()
    data.greatestY = "Player1"
    data.isHit = False
    data.hitCount = 0
    data.bullet = dict()
    
    #scrolling
    data.scrollY = 0
    data.setScrollY = 0
    data.scrollYSpeed = 0
    
    #lobby
    data.isReady = False
    data.isMulti = False
    data.isSingle = False
    
    #images
    data.lobbyButton = None
    data.redButton = None
    data.greenButton = None
    data.readyButton = None
    data.img = None
    data.p1Img = None
    data.p2Img = None
    data.p3Img = None
    data.p4Img = None
    data.mountain = None
    data.instr = None

#sets the button image
#https://i.ytimg.com/vi/FeWlncZfKNY/hqdefault.jpg
def setButtonImage(data):
    data.lobbyButton = Image.open("pictures" + "/" + "button.png")
    data.lobbyButton = data.lobbyButton.resize((data.width//2,data.height//2), Image.ANTIALIAS)
    data.lobbyButton = ImageTk.PhotoImage(data.lobbyButton)
    
def setGreenButton(data):
    data.greenButton = Image.open("pictures" + "/" + "greenButton.png")
    data.greenButton = data.greenButton.resize((data.width//2,data.height//2), Image.ANTIALIAS)
    data.greenButton = ImageTk.PhotoImage(data.greenButton)
    
def setRedButton(data):
    data.redButton = Image.open("pictures" + "/" + "redButton.png")
    data.redButton = data.redButton.resize((data.width,50), Image.ANTIALIAS)
    data.redButton = ImageTk.PhotoImage(data.redButton)
    
def setReadyButton(data):
    data.readyButton = Image.open("pictures" + "/" + "readyButton.png")
    data.readyButton = data.readyButton.resize((data.width,50), Image.ANTIALIAS)
    data.readyButton = ImageTk.PhotoImage(data.readyButton)
    
def setMountBackground(data):
    data.mountain = Image.open("pictures" + "/" + "mountain1.jpg")
    data.mountain = data.mountain.resize((data.width,data.height), Image.ANTIALIAS)
    data.mountain = ImageTk.PhotoImage(data.mountain)
#used for draw platform
#http://moziru.com/images/glitch-clipart-transparent-13.png
def setPlatformImage(data):
    data.img = Image.open("pictures" + "/" + "platform.png")
    data.img = data.img.resize((60,20), Image.ANTIALIAS)
    data.img = ImageTk.PhotoImage(data.img)
    
#used to draw each player
#https://pbs.twimg.com/media/DPue4I-X4AAbWDs.png (w/ photoshop!)
def setPlayer1Image(data,color,dir):
    file = ((str(color) + str(dir) + ".png"))
    data.p1Img = Image.open("pictures" + "/" + file)
    data.p1Img = data.p1Img.resize((50,50), Image.ANTIALIAS)
    data.p1Img = ImageTk.PhotoImage(data.p1Img)
    
def setPlayer2Image(data,color,dir):
    file = ((str(color) + str(dir) + ".png"))
    data.p2Img = Image.open("pictures" + "/" + file)
    data.p2Img = data.p2Img.resize((50,50), Image.ANTIALIAS)
    data.p2Img = ImageTk.PhotoImage(data.p2Img)
    
def setPlayer3Image(data,color,dir):
    file = ((str(color) + str(dir) + ".png"))
    data.p3Img = Image.open("pictures" + "/" + file)
    data.p3Img = data.p3Img.resize((50,50), Image.ANTIALIAS)
    data.p3Img = ImageTk.PhotoImage(data.p3Img)
        
def setPlayer4Image(data,color,dir):
    file = ((str(color) + str(dir) + ".png"))
    data.p4Img = Image.open("pictures" + "/" + file)
    data.p4Img = data.p4Img.resize((50,50), Image.ANTIALIAS)
    data.p4Img = ImageTk.PhotoImage(data.p4Img)
    
def setInstructions(data):
    data.instr = Image.open("pictures" + "/" + "instructions.png")
    data.isntr = data.instr.resize((data.width,data.height), Image.ANTIALIAS)
    data.instr = ImageTk.PhotoImage(data.instr)

def setDoggo(PID):
    if PID == "Player1":
        color = "blackTerry"
    elif PID == "Player2":
        color = "tealTerry"
    elif PID == "Player3":
        color = "greenTerry"
    elif PID == "Player4":
        color = "redTerry"
    return color
    
#probably need to hard code p1img p2img etc.
def drawPlayers(canvas,data):
    sY = data.scrollY
    for player in data.otherStrangers:
        PID = data.otherStrangers[player].PID
        color = setDoggo(PID)
        if data.otherStrangers[player].velocity >= 0:
            dir = "Right"
        else: dir = "Left"
        if PID == "Player1":
            setPlayer1Image(data,color,dir)
            if data.otherStrangers[player].alive:
                canvas.create_image(data.otherStrangers[player].x,
                   data.otherStrangers[player].y+sY,image=data.p1Img,anchor="s")
        elif PID == "Player2":
            setPlayer2Image(data,color,dir)
            if data.otherStrangers[player].alive:
                canvas.create_image(data.otherStrangers[player].x,
                   data.otherStrangers[player].y+sY,image=data.p2Img,anchor="s")
        elif PID == "Player3":
            setPlayer3Image(data,color,dir)
            if data.otherStrangers[player].alive:
                canvas.create_image(data.otherStrangers[player].x,
                   data.otherStrangers[player].y+sY,image=data.p3Img,anchor="s")
        elif PID == "Player4":
            setPlayer4Image(data,color,dir)
            if data.otherStrangers[player].alive:
                canvas.create_image(data.otherStrangers[player].x,
                   data.otherStrangers[player].y+sY,image=data.p4Img,anchor="s")
    color = setDoggo(data.me.PID)
    if data.me.velocity >= 0 : dir = "Right"
    else: dir = "Left"
    if data.me.PID == "Player1":
        setPlayer1Image(data,color,dir)
        canvas.create_image(data.me.x,data.me.y+sY,image=data.p1Img,anchor="s")
    elif data.me.PID == "Player2":
        setPlayer2Image(data,color,dir)
        canvas.create_image(data.me.x,data.me.y+sY,image=data.p2Img,anchor="s")
    elif data.me.PID == "Player3":
        setPlayer3Image(data,color,dir)
        canvas.create_image(data.me.x,data.me.y+sY,image=data.p3Img,anchor="s")
    elif data.me.PID == "Player4":
        setPlayer4Image(data,color,dir)
        canvas.create_image(data.me.x,data.me.y+sY,image=data.p4Img,anchor="s")      
          
# draws all the platforms
def drawPlatforms(canvas,data):
    if data.img == None:
        setPlatformImage(data)
    sY = data.scrollY
    for platform in data.platforms:
        (x,y) = platform.getCoords()
        length = platform.getLength()
        canvas.create_image(x,y+sY,image=data.img,anchor="nw")
        
# create a bullet in mouse pressed
def mousePressed(event, data):
    sY = data.scrollY
    msg = ""
    if data.instructions:
        data.isLobby = True
        data.instructions = False
        
    if data.isLobby:
        if not data.me.isReady:
            if event.x < data.width/2 and event.y > data.height/2:
                data.isSingle = True
                data.isMulti = False
                data.me.mode = "single"
            if event.x > data.width/2 and event.y > data.height/2:
                data.isMulti = True 
                data.isSingle = False
                data.me.mode = "multi"
        if event.y > data.height/2 - 50 and event.y < data.height/2:
            if data.isMulti:
                data.me.isReady = not data.me.isReady
                msg = "playerReady multi\n"
            if data.isSingle:
                data.me.isReady = not data.me.isReady
                msg = "playerReady single\n"
        if event.y > data.height/2 - 100 and event.y < data.height/2 -50:
            data.instructions = True
            data.lobby = False
        
        if (msg != ""):
            print ("sending: ", msg,)
            data.server.send(msg.encode())
            
    
    
    if data.isPlaying and data.canFire:
        data.myBullet = Bullet(data.me.x,data.me.y,event.x,event.y-sY)
        data.fired = True
        data.canFire = False
    
def startGame(data):
    if data.otherStrangers == dict() and data.isMulti:
        return None
        
    if data.isSingle and data.me.isReady:
        data.isPlaying = True
        data.isLobby = False
        
    count = 0
    for player in data.otherStrangers:
        if data.otherStrangers[player].isReady == False:
            break
        count += 1
        if count == len(data.otherStrangers):
            data.isLobby = False
            data.isPlaying = True
    
#using keys to move
def keyPressed(event, data):
    if data.isPlaying:
        if event.keysym == "Left" and data.start:
            data.isAcceleratingLeft = True
            
        elif event.keysym == "Right" and data.start:
            data.isAcceleratingRight = True
    
        elif event.keysym == "Up" and data.start == False:
            data.isJumping = True
            data.start = True
        
#releasing keys
def keyReleased(event, data):
    if event.keysym == "Left":
        data.isAcceleratingLeft = False
    if event.keysym == "Right":
        data.isAcceleratingRight = False    

#function to land on platforms (and then jump again)
def landing(data, player, platform):
    (x,y) = data.me.getCoords()
    (pX,pY) = platform.getCoords()
    length = platform.getLength()
    if x >= pX and x <= pX + length:
        if data.me.canLand() and data.me.lastY() <= pY and y >= pY:
            data.me.placePlayerY(pY)
            data.me.resetJump()
            data.currentPlatform = platform
            sY = data.scrollY
            if data.height - data.me.y - 200 > data.setScrollY:
                data.setScrollY = data.height - data.me.y - 200
                
#get hit by a bullet
def bulletHit(data):
    print("damage %d" %data.me.damage)
    if not data.isHit:
        for player in data.bullet:
            x = data.bullet[player].x
            y = data.bullet[player].y
            pX = data.me.x
            pY = data.me.y
            print("x: %d y: %d pX: %d pY: %d" %(x,y,pX,pY))
            distance = math.sqrt((x-pX)**2+(y-pY)**2)
            print ('distance: %d' %distance)
            if distance < 75:
                damage = random.randrange(5,15)
                direction = data.bullet[player].direction
                data.isHit = True
                data.me.getHit(damage,direction)
    #count for invicibility
    else:
        data.hitCount += 1
        if data.hitCount == 5:
            data.isHit = False
            data.hitCount = 0
            
def bulletTimeCount(data):
    if data.canFire == False:
        data.fireCount += 1
        if data.fireCount == 20:
            data.canFire = True
    
#progresses scrollY 3 frames to the target scrollY
def changeScroll(data):
    if data.setScrollY != data.scrollY and data.scrollYSpeed == 0:
        dif = data.setScrollY - data.scrollY
        data.scrollYSpeed = dif // 3
        print("scrollSpeed: %d" %data.scrollYSpeed)
    data.scrollY += data.scrollYSpeed
    if data.scrollY >= data.setScrollY:
        data.scrollY = data.setScrollY
        data.scrollYSpeed = 0
                
#generates the map (only for the highest Y player) and send to other players
def generateMap(data):
    msg = ""
    stopY = data.me.y - data.height
    startY = data.me.y + int(data.height*4)
    if str(data.me.PID) == str(data.greatestY) or data.me.mode == "single":
        generatePlatform(data.platforms,stopY,data.width,startY)
        msg = "mapGen "
        for platform in data.platforms:
            msg += str(platform)
        msg += " \n"
            
    if (msg != "") and data.me.mode == "multi":
        print ("sending: ", msg,)
        data.server.send(msg.encode())
        
#sets the player with the greatest height
def setGreatestHeight(data):
    greatest = data.me.y
    gPID = data.me.PID
    for player in data.otherStrangers:
        if data.otherStrangers[player].y < greatest:
            greatest = data.otherStrangers[player].y
            gPID = data.otherStrangers[player].PID
        #tiebreak goes to higher PID number
        elif data.otherStrangers[player].y == greatest:
            if ord(data.otherStrangers[player].PID[-1]) < ord(gPID[-1]):
                gPID = data.otherStrangers[player].PID
    data.greatestY = gPID

#sends the bullet to other players
def sendBullet(data):
    msg = ""
    if data.fired:
        data.myBullet.move()
        
    #sends the bullet to other players
    if data.fired:
        x = data.myBullet.x
        y = data.myBullet.y
        lX = data.myBullet.lastX
        lY = data.myBullet.lastY
        directionX = data.myBullet.direction[0]
        directionY = data.myBullet.direction[1]
        msg = "bullet %d %d %d %d %d %d\n" %(x,y,lX,lY,directionX,directionY)
        
    if (msg != "") and data.me.mode == "multi":
        print ("sending: ", msg,)
        data.server.send(msg.encode())
        
#the movement timer fired function for a player
def timerFiredPlayer(data):
    msg = ""
    #move to other side of screen
    data.score = ((-data.me.y + data.height - 200)*100)//100

    if data.me.x > data.width:
        data.me.x = 0
        
    if data.me.x < 0:
        data.me.x = data.width
    
    #calls the landing function for all platforms 
    if data.isJumping:
        data.me.jump()
        reverse = data.platforms[::-1]
        for platform in (reverse):
            landing(data,data.me,platform)
    
    #i feel like this does nothing now, but i'm scared to take it out
    else:
        platform = data.currentPlatform
        (x,y) = data.me.getCoords()
        (pX,pY) = platform.getCoords()
        length = platform.getLength()
        if x <= pX or x >= pX + length:
            data.isFalling = True
            
    #accelerate and stuff
    if data.isAcceleratingLeft:
        data.me.accelerate("left")
        
    if data.isAcceleratingRight:
        data.me.accelerate("right")
        
    if not (data.isAcceleratingLeft or data.isAcceleratingRight or data.isHit):
        data.me.moveFriction()
    
    #move and send your coordinates!
    data.me.move()
    (x,y) = data.me.getCoords()
    msg = "playerCoords %d %d %d %d\n" %(x,y,data.score,data.me.damage)
    
    if (msg != "") and data.me.mode == "multi":
        print ("sending: ", msg,)
        data.server.send(msg.encode())

def killDoggo(data):
    msg = ''
    (x,y) = data.me.getCoords()
    platform = data.currentPlatform
    (pX,pY) = platform.getCoords()
    if y-150 > pY:
        data.isPlaying = False
        data.isDeadSplash = True
        data.me.alive = False
        msg = "doggoDied pY\n"
        
    if (msg != "") and data.me.mode == "multi":
        print ("sending: ", msg,)
        data.server.send(msg.encode())
        
def timerFired(data):
    # timerFired receives instructions and executes them
    while (serverMsg.qsize() > 0):
        msg = serverMsg.get(False)
        try:
            print("received: ", msg, "\n")
            msg = msg.split()
            command = msg[0]
            
            if command == "myIDis":
                myPID = msg[1]
                data.me.changePID(myPID)
            
            elif command == "newPlayer":
                newPID = msg[1]
                x = data.width/2
                y = data.height/2
                data.otherStrangers[newPID] = Player(newPID, x, y)
                
            elif command == "playerReady":
                PID = msg[1]
                data.otherStrangers[PID].mode = msg[2]
                status = not data.otherStrangers[PID].isReady
                data.otherStrangers[PID].isReady = status
                if msg[2] == "single":
                    data.otherStrangers[PID].y = 10000
    
            elif command == "playerCoords":
                PID = msg[1]
                x = int(msg[2])
                y = int(msg[3])
                score = int(msg[4])
                dmg = int(msg[5])
                data.otherStrangers[PID].x = x
                data.otherStrangers[PID].y = y
                data.otherStrangers[PID].score = score
                data.otherStrangers[PID].damage = dmg
                
            elif command == "mapGen":
                #will be in the form of "123,321;789,987;"
                PID = msg[1]
                msg[2] = msg[2][0:-1] #remove the last ';'
                l = msg[2].split(";") #['123,321','789,987']
                data.platforms = []
                for c in l:
                    coords = c.split(",")
                    x = int(coords[0])
                    y = int(coords[1])
                    data.platforms += [Platform(x,y)]
                    
            elif command == "bullet":
                PID = msg[1]
                x = int(msg[2])
                y = int(msg[3])
                lX = int(msg[4])
                lY = int(msg[5])
                dirX = int(msg[6])
                dirY = int(msg[7])
                data.bullet[PID] = Bullet(x,y)
                data.bullet[PID].lastX = lX
                data.bullet[PID].lastY = lY
                data.bullet[PID].direction = (dirX,dirY)
            
            elif command == "doggoDied":
                PID = msg[1]
                height = msg[2]
                data.otherStrangers[PID].score = height
                data.otherStrangers[PID].alive = False
                
            elif command == "left":
                PID = msg[1]
                del data.otherStrangers[PID]
        except:
            print("Failed")
        serverMsg.task_done()

def redrawAll(canvas, data):
    if data.instructions:
        setInstructions(data)
        canvas.create_image(0,0,image = data.instr, anchor = 'nw')
    if data.isLobby and data.instructions == False:
        #role selection
        if data.lobbyButton == None:
            setButtonImage(data)
            setRedButton(data)
            setGreenButton(data)
            setReadyButton(data)
        if data.isSingle:
            button = data.greenButton
        else: button = data.lobbyButton
        canvas.create_image(0,data.height/2,image=button,anchor='nw')
        if data.isMulti:
            button = data.greenButton
        else: button = data.lobbyButton
        canvas.create_image(data.width/2,data.height/2,image=button,
                            anchor='nw')
                            
        canvas.create_text(data.width*(3/4),data.height*(3/4), 
                        text="Click to play with others!",font="Helvetica 12")
        canvas.create_text(data.width*(1/4),data.height*(3/4),
                        text = "Click to play single!", font="Helvetica 12")
        canvas.create_image(0,data.height//2-100,image=data.readyButton,
                                anchor = 'nw')     
        canvas.create_text(data.width/2,data.height/2-75, text="Help")
        if data.me.isReady == True:
            canvas.create_image(0,data.height//2-50,image=data.readyButton,
                                anchor = 'nw')
        else: 
            canvas.create_image(0,data.height//2-50,image=data.redButton,
                                anchor = 'nw')
        canvas.create_text(data.width/2,data.height/2-25, text="ready?")
        # other player
        canvas.create_text(10,70,text="Other Players:", font="Helvetica 12", 
                            anchor = NW)
        i = 1
        for item in (data.otherStrangers):
            canvas.create_text(10,90+20*i,text = (data.otherStrangers[item].PID)+
                            " playing as: " + data.otherStrangers[item].mode, 
                            font="Helvetica 12", anchor = NW)
            i += 1
        # me
        name = data.me.PID
        canvas.create_text(10,30,text="My name is: "+ name + " playing as: " + 
                            data.me.mode, font="Helvetica 12",anchor = NW)
        canvas.create_text(10,50,text="Changing name to: " + data.nameChange,
                            font="Helvetica 12", anchor = NW)
    sY = data.scrollY

    if data.isPlaying:
        drawPlatforms(canvas,data)
        drawPlayers(canvas,data)
        if data.me.mode == "multi":
            for player in data.otherStrangers:
                PID = data.otherStrangers[player].PID
                dmg = data.otherStrangers[player].damage
                if PID == "Player1":
                    canvas.create_image(data.width/5, data.height-100,image=data.p1Img)
                    canvas.create_text(data.width/5,data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
                if PID == "Player2":
                    canvas.create_image(data.width*(2/5), data.height-100,image=data.p2Img)
                    canvas.create_text(data.width*(2/5),data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
                elif PID == "Player3":
                    canvas.create_image(data.width*(3/5), data.height-100,image=data.p3Img)
                    canvas.create_text(data.width*(3/5),data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
                elif PID == "Player4":
                    canvas.create_image(data.width*(4/5), data.height-100,image=data.p4Img)
                    canvas.create_text(data.width*(4/5),data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
            dmg = data.me.damage
            if data.me.PID == "Player1":
                    canvas.create_image(data.width/5, data.height-100,image=data.p1Img)
                    canvas.create_text(data.width/5,data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
            elif data.me.PID == "Player2":
                    canvas.create_image(data.width*(2/5), data.height-100,image=data.p2Img)
                    canvas.create_text(data.width*(2/5),data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
            elif data.me.PID == "Player3":
                    canvas.create_image(data.width*(3/5), data.height-100,image=data.p3Img)
                    canvas.create_text(data.width*(3/5),data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
            elif data.me.PID == "Player4":
                    canvas.create_image(data.width*(4/5), data.height-100,image=data.p4Img)
                    canvas.create_text(data.width*(4/5),data.height-100,text=str(dmg)+"%",
                                        font="Helvetica 20",fill="white")
        

        canvas.create_text(20,20,text=str(data.score),font="Helvetica 12", anchor = NW)
    # draw bullets
        if data.myBullet != None:
            canvas.create_oval(data.myBullet.x-5,data.myBullet.y-5+sY,
                        data.myBullet.x+5,data.myBullet.y+5+sY,fill='green')
        for player in data.bullet:
            bullet = data.bullet[player]
            x = bullet.x
            y = bullet.y
            canvas.create_oval(x-5,y-5+sY,x+5,y+5+sY,fill="yellow")
        
    if data.isDeadSplash:
        canvas.create_text(data.width/2,data.height/2, text = "You Died! Score: %d" %(data.score),
                            font = "Helvetica 24")
        canvas.create_text(data.width/2,data.height*(3/4), text = "Click anywhere to spectate",
                            font = "Helvetica 12")
        
####################################
# use the run function as-is
####################################

def run(width, height, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        if data.mountain == None:
            setMountBackground(data)
        canvas.create_image(0,0,image=data.mountain,anchor = 'nw')
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        #redrawAllWrapper(canvas, data)
        
    def keyReleaseWrapper(event, canvas, data):
        keyReleased(event, data)
        redrawAllWrapper(canvas,data)

    def timerFiredWrapper(canvas, data):
        if data.isLobby:
            timerFired(data)
            if data.me.isReady:
                startGame(data)
        if data.isPlaying and data.me.mode == "multi":
            timerFiredPlayer(data)
            changeScroll(data)
            timerFired(data)
            setGreatestHeight(data)
            generateMap(data)
            sendBullet(data)
            bulletTimeCount(data)
            killDoggo(data)
            bulletHit(data)
        if data.isPlaying and data.me.mode == "single":
            data.otherStrangers = dict()
            timerFiredPlayer(data)
            changeScroll(data)
            sendBullet(data)
            bulletTimeCount(data)
            generateMap(data)
            killDoggo(data)
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
    msg="left rip\n"
    if (msg != ""):
        print ("sending: ", msg,)
        data.server.send(msg.encode())
    print("bye!")

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()

run(400, 600, serverMsg, server)