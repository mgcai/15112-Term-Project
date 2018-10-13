#Player class
#some init vars are now useless
import math

class Player(object):
        
    def __init__(self, PID, x, y, damage=0,mode="lobby"):
        self.PID = PID
        self.UID = PID
        self.x = x
        self.y = y
        self.mode = mode
        self.damage = damage
        self.jumpVelocity = 0
        self.jumpAcceleration = -10
        self.jumpPower = 75
        self.maxVelocity = 40
        self.startVelocity = 10
        self.acceleration = 2
        self.velocity = 0
        self.airDrag = -1
        self.friction = -5
        self.isJumping = False
        self.isMoving = False
        self.isReady = False
        self.score = -y
        self.alive = True
        
    def changePID(self, PID):
        self.PID = PID
        
    def getHit(self,damage,direction):
        self.damage += damage
        knockback = (self.damage/10)
        self.velocity = 0
        self.jumpVelocity = 0
        dx = direction[0]
        dy = direction[1]
        distance = int(math.sqrt(dx**2 + dy**2))
        factor = (self.maxVelocity/2) / distance
        knockbackX = dx*factor
        knockbackY = dy*factor
        self.velocity += knockbackX
        self.jumpVelocity += knockbackY

    def accelerate(self,direction):
        if direction == "left":
            if self.velocity >= 0:
                self.velocity = -self.startVelocity
            self.velocity -= self.acceleration
        if direction == "right":
            if self.velocity <= 0:
                self.velocity = self.startVelocity
            self.velocity += self.acceleration
        if self.velocity > self.maxVelocity: self.velocity = self.maxVelocity
        if self.velocity < -self.maxVelocity: self.velocity = -self.maxVelocity
        
    def move(self):
        self.x += self.velocity
        
    def moveFriction(self):
        if self.velocity > 0:
            self.velocity += self.friction
            if self.velocity < 0: self.velocity = 0
        elif self.velocity < 0:
            self.velocity -= self.friction
            if self.velocity > 0: self.velocity = 0

    def getIsMoving(self):
        return self.isMoving
        
    def placePlayerY(self, y):
        self.y = y
        
    def canLand(self):
        if self.jumpVelocity <= 0:
            return True
        return False
    
    def lastY(self):
        return self.y + self.jumpVelocity
    
    def jump(self):
        if self.isJumping == False:
            self.jumpVelocity = self.jumpPower
            self.isJumping = True
        self.jumpVelocity += self.jumpAcceleration
        self.y -= self.jumpVelocity
        
    def resetJump(self):
        self.jumpVelocity = 0
        self.isJumping = False
            
    def getCoords(self):
        return (self.x,self.y)