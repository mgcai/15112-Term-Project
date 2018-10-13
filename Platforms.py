#the platform class used for platforms in the game
class Platform(object):
    
    def __init__(self,x,y,length=60):
        self.x = x
        self.y = y
        self.length = length
        
    def getCoords(self):
        return (self.x,self.y)
        
    def getLength(self):
        return self.length
        
    def __eq__(self, other):
        return isinstance(other,Platform) and self.x == other.x and \
                self.y == other.y and self.length == other.length
                
    #repr is formatted like this for easier communication of mapGen
    def __repr__(self):
        return "%d,%d;" %(self.x,self.y)
        
    def getHashables(self):
        return (self.x,self.y)
        
    def __hash__(self):
        return hash(self.getHashables())