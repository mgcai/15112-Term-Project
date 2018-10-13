import random
from Platforms import Platform

def generatePlatform(platforms, stopY, width, startY):
    lastPlatform = platforms[-1]
    if lastPlatform.y < stopY:
        return platforms
    else:
        while platforms[0].y > startY:
            platforms.pop(0)
        y = lastPlatform.y
        
        rX = random.randrange(10,width-40)
        rY = random.randrange(-70,-10)
        platforms += [Platform(rX,y+rY)]
        return generatePlatform(platforms,stopY,width,startY)
    