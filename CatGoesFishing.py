import numpy as np 
from enum import Enum
from cmu_graphics import *
import math

def vec(x, y):
    return np.array([x, y])

G = 10000
FPS = 60
DT = 1/60
catPos = vec(500, 500)
fishingRodLength = 100

#defines vectors


def distance(v1, v2):
    distVector = v1-v2
    return np.dot(distVector, distVector)**0.5

class State(Enum):
    REST = 1
    LOAD = 2
    CAST = 3
    REEL = 4
        
class Hook():
    def __init__(self):
        self.state = State.REST
        self.r = 10
        self.f = vec(0, 0)
        self.m = 10
        self.theta = 0 #radians
        self.loadDir = 'backwards'
        self.pos = vec(catPos[0] + fishingRodLength*math.cos(self.theta), catPos[1] + fishingRodLength*math.sin(self.theta))
        
        #used for verlet integration
        self.v = vec(0,0)
        self.prevPos = self.pos - (self.v * DT)
    
    def cycleState(self):
        self.state = State((self.state.value % 4) + 1)
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

    def castHelper(self):
        a = self.f / self.m
        if self.loadDir == 'backwards':
            self.v[0] = -math.pi*fishingRodLength/25/DT
        else:
            self.v[0] = math.pi*fishingRodLength/25/DT
        self.v = self.v + a * DT

        self.prevPos = self.pos
        self.pos = self.pos + (self.v * DT)

        print(self.f, self.v, self.pos)
        self.f = vec(0,0)
            
    def addGravity(self):
        self.f += vec(0, int(G))

    def reelHelper(self):
        pass

    def verletUpdate(self):
        if self.state == State.REST: #do nothing (for now..)
            pass
        elif self.state == State.LOAD: #polar
            self.loadHelper()
        elif self.state == State.CAST: #kinematics
            self.addGravity()
            self.castHelper()
        elif self.state == State.REEL: #polar
            self.v = vec(0,0)
            pass

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawCircle(float(x), float(y), self.r)
    
    def __repr__(self):
        return(self.state.name)


def onAppStart(app):
    app.width, app.height = 3840, 2160
    app.paused = False
    app.hook = Hook()
    app.stepsPerSecond = 60
    resetApp(app)

def resetApp(app):
    app.objects = []

def onStep(app):
    if app.paused: return
    app.hook.verletUpdate()
    print(app.hook.theta)

def onKeyPress(app, key):
    if 'space' in key:
        app.hook.cycleState()
        print(app.hook)

def onKeyRelease(app, key): #can implement REAL fishing later...
    pass

def onMousePress(app, mouseX, mouseY):
    pass
def onMouseRelease(app, mouseX, mouseY):
    pass

def redrawAll(app):
    #Draw Cat
    catX, catY = catPos[0], catPos[1]
    drawRect(float(catX), float(catY), 100, 100, align = 'center')
    #Draw Hook
    app.hook.draw()


def main():
    cmu_graphics.runApp()

main()