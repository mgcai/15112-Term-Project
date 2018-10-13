from Platforms import Platform
# events-example0.py
# Barebones timer, mouse, and keyboard events

from tkinter import *
import random
from Player import Player
from mapGen import generatePlatform
####################################
# customize these functions
####################################

def init(data):
    data.finishPlatform = Platform(0,5,40)
    data.bottomPlatform = Platform(0,data.height-5,data.width)
    data.platforms = [data.bottomPlatform,data.finishPlatform]
    data.powerPlatform = Platform(data.width-40,5,40)
    data.otherPlatforms = [data.bottomPlatform,data.powerPlatform]
    data.scrollMargin = 30
    data.player = Player(data.width-data.scrollMargin,data.height-10)
    data.scrollx = 0
    data.scrolly = 0
    data.testPlatform = Platform(data.width-(2*data.scrollMargin),data.height-30,40)
    data.bottomPlatform = Platform(0,data.height-5,data.width*3)
    data.isJumping = False
    data.isAcceleratingRight = False
    data.isAcceleratingLeft = False
    data.isFalling = False
    data.currentPlatform = data.bottomPlatform


def generatePlatform(platforms):
    bottom = platforms[0]
    lastPlatform = platforms[-1]
    if lastPlatform.y > bottom.y+20:
        return platforms
    else:
        x = lastPlatform.x
        y = lastPlatform.y
        rX = 0
        rY = 0
        while abs(rX) < 20:
            rX = random.randrange(-10,30)
        while abs(rY) < 20:
            rY = random.randrange(-10,30)
        platforms += [Platform(x+rX,y+rY)]
        return generatePlatform(platforms)
    # load data.xyz as appropriate
    
def generatePlatformPowerUp(platforms):
    bottom = platforms[0]
    lastPlatform = platforms[-1]
    if lastPlatform.y > bottom.y+20:
        return platforms
    else:
        x = lastPlatform.x
        y = lastPlatform.y
        rX = 0
        rY = 0
        while abs(rX) < 5:
            rX = random.randrange(-30,10)
        while abs(rY) < 5:
            rY = random.randrange(-10,30)
        platforms += [Platform(x+rX,y+rY)]
        return generatePlatformPowerUp(platforms)

def keyPressed(event, data):
    if event.keysym == "Left":
        data.isAcceleratingLeft = True
    elif event.keysym == "Right":
        data.isAcceleratingRight = True
    elif event.keysym == "Up":
        data.isJumping = True

def keyReleased(event, data):
    if event.keysym == "Left":
        data.isAcceleratingLeft = False
    if event.keysym == "Right":
        data.isAcceleratingRight = False

def timerFired(data):
    generatePlatform(data.platforms)
    generatePlatformPowerUp(data.otherPlatforms)
    data.platforms += data.otherPlatforms
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
    
    data.player.move()
        
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
            
def redrawAll(canvas, data):
    (x,y) = data.player.getCoords()
    canvas.create_oval(x-5,y-5,x+5,y+5,fill="blue")
    for platform in data.platforms:
        (x,y) = platform.getCoords()
        length = platform.getLength()
        canvas.create_rectangle(x,y,x+length,y+2,fill="black")
    pass

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
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

run(400, 400)