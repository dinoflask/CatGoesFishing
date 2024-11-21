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



def onAppStart(app):
    app.width, app.height = 3840, 2160
    app.paused = False
    app.hook = Hook()
    app.stepsPerSecond = 60
    resetApp(app)


def resetApp(app):
    app.objects = [app.hook]


class rodState(Enum):
    REST = 1
    CAST = 2
    REEL = 3

class Rod(Hook):

    def __init__(self, f, theta, loadDir, pos):
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
    

def onStep(app):
    if app.paused: return
    for object in app.objects:
        object.eulerUpdate()
    

def onKeyPress(app, key):
    if 'space' in key:
        app.hook.cycleState()
        if app.hook.state == hookState.CASTED:
            app.objects.append(Rod(app.hook.f, app.hook.theta, app.hook.loadDir, app.hook.pos))
        

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
    drawRect(600, 650, 1000, 500, fill='blue') #ocean
    drawRect(600, 550, 1000, 500, fill='green', align='right-top')
    #Draw Hook and Rod
    for object in app.objects:
        object.draw()


def main():
    cmu_graphics.runApp()

main()