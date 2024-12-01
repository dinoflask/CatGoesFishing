import numpy as np 
from enum import Enum
from cmu_graphics import *
import math
import random

def vec(x, y):
    return np.array([x, y])

G = 10000
FPS = 60
DT = 1/60
catPos = vec(500, 500) #The Cat will move later, and it will not be a global variable.
fishingRodLength = 110

def distance(v1, v2):
    distVector = v1-v2
    return np.dot(distVector, distVector)**0.5

class rodState(Enum):
    REST = 1
    LOAD = 2
    CASTED = 3
    PULL = 4

class Rod():

    def __init__(self):
        self.hook = None
        self.state = rodState.REST
        self.r = 10
        self.f = vec(0, 0)
        self.m = 10
        self.theta = 0 #radians
        self.loadDir = 'backwards'
        self.pos = vec(catPos[0] + fishingRodLength, catPos[1])
        #used for euler integration
        self.v = vec(0,0)

        
    def cycleState(self):
        
        self.state = rodState((self.state.value % 4) + 1)
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
  
    def castedHelper(self):
        if self.hook.theta <= -math.pi/2:
                self.cycleState()
        if self.theta > 0: #let the rod stop undulating
                self.theta -= math.pi/25
                self.pos = vec(catPos[0] + fishingRodLength*math.cos(self.theta), catPos[1] - fishingRodLength*math.sin(self.theta))

    def pullHelper(self):
        if self.hook.pos[1] <= catPos[1]:
            self.hook = None
            self.cycleState()

    def eulerUpdate(self):
        if self.state == rodState.REST: #do nothing (for now..)
            pass
        elif self.state == rodState.LOAD: #polar
            self.loadHelper()
        elif self.state == rodState.CASTED:
            self.castedHelper()
        elif self.state == rodState.PULL:
            self.pullHelper()

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawCircle(float(x), float(y), self.r)
        drawLine(float(x), float(y), int(catPos[0]), int(catPos[1]))
        if self.hook != None:
            drawLine(float(x), float(y), int(self.hook.pos[0]), int(self.hook.pos[1]))
    
    def __repr__(self):
        return(self.state.name)

class hookState(Enum):
    #I got the idea of using multiple states ("state control") to handle the 
    #changing behavior of the fishing rod, from Vincent Boling, Class of 2028, Physics.
    PULL = 1
    CAST = 2
    REEL = 3

class Hook():

    def __init__(self, f, theta, loadDir, pos):
        self.state = hookState.CAST
        self.r = 10
        self.m = 10
        self.f = f
        self.theta = -math.pi/10 #radians
        self.loadDir = loadDir
        self.pos = pos
        
        #used for euler intergration
        self.v = vec(0,0) 
        
    def cycleState(self):
        self.state = hookState((self.state.value % 3) + 1)
        return self.state
    
    def pullHelper(self):
        if self.pos[1] >= catPos[1]:
                self.pos -= vec(0, 10)
    
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

    def reelHelper(self):
        if self.theta <= -math.pi/2:
            self.cycleState()

        rodPos = (catPos[0] + fishingRodLength, catPos[1])
        reelRadius = distance(rodPos, self.pos)
        if self.theta > -math.pi/2:
            self.theta -= math.pi/100
            self.pos = vec(rodPos[0] + reelRadius*math.cos(self.theta), rodPos[1] - reelRadius*math.sin(self.theta))

    def addGravity(self):
        self.f += vec(0, int(G))

    def eulerUpdate(self):
        if self.state == hookState.PULL: #do nothing (for now..)
            self.pullHelper()
        elif self.state == hookState.CAST: #kinematics
            self.addGravity()
            self.castHelper()
        elif self.state == hookState.REEL: #polar
            self.reelHelper()

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawCircle(float(x), float(y), self.r)
        #drawLine(float(x), float(y), int(Hook.pos[0]), int(Hook.pos[1]))

    def __repr__(self):
        return(self.state.name)

class fishState(Enum):
    IDLE = 1
    AGITATED = 2
    CAUGHT = 3

class Fish():
    def __init__(self):
        self.state = fishState.IDLE
        self.pos = vec(1100, 700)
        self.theta = 0 #degrees
        self.size = 20
        self.theta = 0

    def cycleState(self):
        self.state = fishState((self.state.value % 3) + 1)
        return self.state
    
    def moveHelper(self):
        if self.state == fishState.IDLE:
            self.theta = random.random() * (2*math.pi)
            self.pos += vec(100*self.theta, 100*self.theta)
            print(self.theta, self.pos)
        elif self.state == fishState.AGITATED:
            pass
            #move towards bait
        elif self.state == fishState.CAUGHT:
            self.pos = app.hook.pos

    def eulerUpdate(self):
        self.moveHelper()

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawCircle(float(x), float(y), self.size, fill = 'orange')
        #drawLine(float(x), float(y), int(Hook.pos[0]), int(Hook.pos[1]))

def onAppStart(app):
    app.width, app.height = 3840, 2160
    app.paused = False
    app.rod = Rod()
    app.stepsPerSecond = 6

    #app.startMenu = True
    #app.shopMenu = False
    #app.journalMenu = False
    #app.tutorial1 = False

    resetApp(app)

def resetApp(app):
    app.objects = [app.rod, Fish()]

def onStep(app):
    if app.paused: return    
    for object in app.objects:
        object.eulerUpdate()
    
    
def onKeyPress(app, key):
    if 'space' in key:
        app.rod.cycleState()
        if app.rod.state == rodState.CASTED: #Create a new hook object when you cast your rod
            if app.rod.hook == None:
                app.rod.hook = Hook(app.rod.f, app.rod.theta, app.rod.loadDir, app.rod.pos)
            app.objects.append(app.rod.hook)
        if app.rod.hook != None and app.rod.hook.state == rodState.PULL: #Reset app.rod's hook object after you pull the Fish in
            app.objects.pop()
            app.rod.hook = None
        

def onKeyRelease(app, key):
    pass
def onMousePress(app, mouseX, mouseY):
    pass

def redrawAll(app):
    #Draw Menus
    #if app.startMenu == True:

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


