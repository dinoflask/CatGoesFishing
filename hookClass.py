import numpy as np 
from cmu_graphics import *
import math
from enum import Enum
from rodClass import *

class hookState(Enum):
    REST = 1
    LOAD = 2
    CASTED = 3

class Hook():

    def __init__(self):
        self.state = hookState.REST
        self.r = 10
        self.f = vec(0, 0)
        self.m = 10
        self.theta = 0 #radians
        self.loadDir = 'backwards'
        self.pos = vec(catPos[0] + fishingRodLength, catPos[1])
        #used for euler integration
        self.v = vec(0,0)
        
    
    def cycleState(self):
        self.state = hookState((self.state.value % 3) + 1)
        return self.state

    def loadHelper(self):
        if self.theta > math.pi:
            self.loadDir = 'forwards'
        if self.theta < 0:
            self.loadDir = 'backwards'
        if self.loadDir == 'backwards':
            self.theta += math.pi/25
        if self.loadDir == 'forwards':
            self.theta -= math.pi/25
        self.pos = vec(catPos[0] + fishingRodLength*math.cos(self.theta), catPos[1] - fishingRodLength*math.sin(self.theta))
  

    def eulerUpdate(self):
        if self.state == hookState.REST: #do nothing (for now..)
            pass
        elif self.state == hookState.LOAD: #polar
            self.loadHelper()
        elif self.state == hookState.CASTED:
            while self.theta > 0:
                self.theta -= math.pi/25
                self.pos = vec(catPos[0] + fishingRodLength*math.cos(self.theta), catPos[1] - fishingRodLength*math.sin(self.theta))
            

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawCircle(float(x), float(y), self.r)
        drawLine(float(x), float(y), int(catPos[0]), int(catPos[1]))
    
    def __repr__(self):
        return(self.state.name)