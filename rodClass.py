import numpy as np 
from cmu_graphics import *
import math
from enum import Enum
from hookClass import *

class rodState(Enum):
    REST = 1
    CAST = 2
    REEL = 3

class Rod():

    def __init__(self, f, theta, loadDir, pos):
        self.hook = Hook()
        self.state = rodState.CAST
        self.r = 10
        self.m = 10
        self.f = f
        self.theta = theta #radians
        self.loadDir = loadDir
        self.pos = pos
        
        #used for euler intergration
        self.v = vec(0,0) #depends on the rest of this stuff
        
    
    def cycleState(self):
        self.state = rodState((self.state.value % 3) + 1)
        return self.state
    
    def castHelper(self):
        if self.pos[1] > 650:
            self.cycleState()
        a = self.f / self.m
        if self.loadDir == 'backwards':
            self.v[0] = -math.pi*fishingRodLength/25/DT
        else:
            self.v[0] = math.pi*fishingRodLength/25/DT
        self.v = self.v + a * DT
        self.pos = self.pos + (self.v * DT)
        self.f = vec(0,0)

    def addGravity(self):
        self.f += vec(0, int(G))

    def eulerUpdate(self):
        if self.state == rodState.REST: #do nothing (for now..)
            pass
        elif self.state == rodState.CAST: #kinematics
            self.addGravity()
            self.castHelper()
        elif self.state == rodState.REEL: #polar
            self.v = vec(0,0)

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawCircle(float(x), float(y), self.r)
        #drawLine(float(x), float(y), int(Hook.pos[0]), int(Hook.pos[1]))

    def __repr__(self):
        return(self.state.name)
    
