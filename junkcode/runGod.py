# events-example0.py
# Barebones timer, mouse, and keyboard events

from tkinter import *
from Player import Player
from Platforms import Platform
from weather import weather

####################################
# customize these functions
####################################

def init(data):
    # load data.xyz as appropriate
    data.gameWeather = weather(0)
    data.scrollMargin = 30
    data.player = Player(data.width-data.scrollMargin,data.height-10)
    data.testPlatform = Platform(data.width-(2*data.scrollMargin),data.height-30,40)
    data.bottomPlatform = Platform(0,data.height-5,data.width)
    data.platforms = [data.testPlatform, data.bottomPlatform]
    data.canRain = True
    data.canLightning = True
    data.willLightning = False
    data.isLightning = False
    data.lightning = None
    data.lightningCounter = 0
    data.timeCount = 0

def mousePressed(event, data):
    # use event.x and event.y
    if data.canLightning:
        data.canLightning = False
        data.willLightning = True
        data.lightning = event.x
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    if event.keysym == "Left":
        data.gameWeather.windSpeed(-1)
    elif event.keysym == "Right":
        data.gameWeather.windSpeed(1)
    
def timerFired(data):
    if data.willLightning == True:
        data.lightningCounter += 1
    if data.lightningCounter == 5:
        data.isLightning = True
    if data.lightningCounter == 20:
        data.lightning = None
        data.isLightning = False
    if data.lightningCounter == 40:
        data.lightningCounter = 0
        data.canLightning = True
        data.willLightning = False
        
    print (data.lightningCounter)

def redrawAll(canvas, data):
    (x,y) = data.player.getCoords()
    canvas.create_oval(x-5,y-5,x+5,y+5,fill="blue")
    if data.lightning != None and data.isLightning:
        canvas.create_rectangle(data.lightning-2,0,data.lightning+2,data.height,
                                fill="yellow")
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
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(400, 200)