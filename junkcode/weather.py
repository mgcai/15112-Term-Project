class weather(object):
    def __init__(self, wind):
        self.wind = wind
        self.maxWind = 10
        self.rain = False
        self.thunder = False
    
    def windSpeed(self,change):
        self.wind += self.wind
        if self.wind > self.maxWind or self.wind < -self.maxWind:
            self.wind = self.maxWind
        
    def makeItRain(self):
        self.rain = True
        
    def makeItThunder(self):
        self.thunder = True