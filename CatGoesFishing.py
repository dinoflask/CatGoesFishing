import numpy as np 
from cmu_graphics import *

G = 9.8
FPS = 100
DT = 1/FPS

#defines vectors
def vec(x, y):
    return np.array([x, y])

def distance(v1, v2):
    distVector = v1-v2
    return np.dot(distVector, distVector)**0.5

catPos = vec(500, 500)
class State:
    def __init__(self, num): #Use Enum
        if num == 1:
            self.state = 'REST'
        if num == 2:
            self.state = 'LOAD'
        if num == 3:
            self.state = 'CAST'
        if num == 4:
            self.state = 'REEL'

class Particle:
    def __init__(self):
        self.state = State(1).state
        self.pos = vec(catPos[0] + 200, catPos[1])
        self.r = 10
        self.theta = 0 #radians

    def rest(self):
        self.state = State(1).state

    def load(self):
        self.state = State(2).state

    def cast(self):
        self.state = State(3).state

    def reel(self):
        self.state = State(4).state

    def verletUpdate(self):
        if self.state == 'REST': #do nothing (for now..)
            pass
        elif self.state == 'LOAD': #polar
            pass
        elif self.state == 'CAST': #kinematics
            pass
        elif self.state == 'REEL': #polar
            pass

        #verlet update down here

    

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawCircle(float(x), float(y), self.r)


def onAppStart(app):
    app.width, app.height = 1920, 1080
    app.paused = False
    app.hook = Particle()
    resetApp(app)

def resetApp(app):
    app.particles = []

def onStep(app):
    if app.paused: return
    app.hook.verletUpdate()

def redrawAll(app):
    #Draw Cat
    catX, catY = catPos[0], catPos[1]
    drawRect(float(catX), float(catY), 100, 100)
    #Draw Hook
    app.hook.draw()

cmu_graphics.runApp()