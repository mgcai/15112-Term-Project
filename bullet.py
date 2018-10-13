import math

#bullet class, allows for movement
class Bullet(object):
    
    def __init__(self,x,y,clickX=0,clickY=0):
        self.x = x
        self.y = y
        self.lastX = None
        self.lastY = None
        self.speed = 30
        self.direction = (clickX - x, clickY - y)
        
    def move(self):
        dx = self.direction[0]
        dy = self.direction[1]
        distance = int(math.sqrt(dx**2 + dy**2))
        factor = self.speed / distance
        self.lastX = self.x
        self.lastY = self.y
        self.x += int(dx*factor)
        self.y += int(dy*factor)
        
    def __repr__(self):
        return "%d,%d;" %(self.x,self.y)
    