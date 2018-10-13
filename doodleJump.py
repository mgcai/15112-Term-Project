# python -m pip install pillow
# kyle's dots example used as starter code, thanks kyle!

from tkinter import *
from Player import Player
from bullet import Bullet
from Platforms import Platform
from mapGen import generatePlatform
from PIL import ImageGrab, ImageTk, Image

####################################
# customize these functions
####################################

def init(data):
    data.scrollMargin = 30
    data.player = Player("me",data.width-data.scrollMargin,data.height-10)
    data.scrollY = data.height - data.player.y - 50
    data.testPlatform = Platform(data.width-(2*data.scrollMargin),data.height-15,40)
    data.bottomPlatform = Platform(0,data.height-5,data.width)
    data.platforms = [data.testPlatform, data.bottomPlatform]
    data.isJumping = False
    data.isAcceleratingRight = False
    data.isAcceleratingLeft = False
    data.isFalling = False
    data.scrollY = 0
    data.start = False
    data.currentPlatform = data.bottomPlatform
    data.fired = False
    data.bullet = dict()
    data.img = None
    
def setPlatformImage(data):
    data.img = Image.open("platform.png")
    data.img = data.img.resize((60,20), Image.ANTIALIAS)
    data.img = ImageTk.PhotoImage(data.img)
    
def drawPlatforms(canvas,data):
    setPlatformImage(data)
    sY = data.scrollY
    for platform in data.platforms:
        (x,y) = platform.getCoords()
        length = platform.getLength()
        canvas.create_image(x,y+sY,image=data.img,anchor="nw")
        
def mousePressed(event, data):
    # use event.x and event.y
    sY = data.scrollY
    data.bullet[data.player.PID] =\
                        Bullet(data.player.x,data.player.y,event.x,event.y-sY)
    data.fired = True

def keyPressed(event, data):
    if event.keysym == "Left":
        data.isAcceleratingLeft = True
        
    if event.keysym == "Right":
        data.isAcceleratingRight = True

    elif event.keysym == "Up" and data.start == False:
        data.isJumping = True
        data.start = True
        
def keyReleased(event, data):
    if event.keysym == "Left":
        data.isAcceleratingLeft = False
    if event.keysym == "Right":
        data.isAcceleratingRight = False    

def landing(data, player, platform):
    (x,y) = player.getCoords()
    (pX,pY) = platform.getCoords()
    length = platform.getLength()
    if x >= pX and x <= pX + length:
        if player.canLand() and player.lastY() <= pY and y >= pY:
            player.placePlayerY(pY-5)
            player.resetJump()
            data.currentPlatform = platform
            sY = data.scrollY
            if data.height - data.player.y - 50 > sY:
                data.scrollY = data.height - data.player.y - 50

def timerFired(data):
    print (data.platforms)
    if data.player.x > data.width:
        data.player.x = 0
    if data.player.x < 0:
        data.player.x = data.width
        
    ######################################################
    # Fix this
    # pretty fixed
    stopY = data.player.y - data.height
    startY = data.player.y + int(data.height*(1.5))
    generatePlatform(data.platforms,stopY,data.width,startY)
    ########################################################
    
    if data.isJumping:
        data.player.jump()
        reverse = data.platforms[::-1]
        for platform in (reverse):
            landing(data,data.player,platform)
        
    else:
        platform = data.currentPlatform
        (x,y) = data.player.getCoords()
        (pX,pY) = platform.getCoords()
        length = platform.getLength()
        if x <= pX or x >= pX + length:
            data.isFalling = True
            
    if data.isAcceleratingLeft:
        data.player.accelerate("left")
        
    if data.isAcceleratingRight:
        data.player.accelerate("right")
        
    if not (data.isAcceleratingLeft or data.isAcceleratingRight):
        data.player.moveFriction()
    
    data.player.move()
    
    if data.fired:
        data.bullet[data.player.PID].move()
    
    
def redrawAll(canvas, data):
    (x,y) = data.player.getCoords()
    sY = data.scrollY
    canvas.create_oval(x-5,y-5+sY,x+5,y+5+sY,fill="blue")
    drawPlatforms(canvas,data)
    for player in data.bullet:
        bullet = data.bullet[player]
        x = bullet.x
        y = bullet.y
        canvas.create_oval(x-5,y-5+sY,x+5,y+5+sY,fill="red")
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
        #redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        #redrawAllWrapper(canvas, data)
        
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

run(400, 600)