import numpy as np 
from enum import Enum
from cmu_graphics import *
import math
import random

#This function is from physics TA mini-lecture.
def vec(x, y):
    return np.array([x, y])

G = 10000
FPS = 60
DT = 1/60

#This function is from physics TA mini-lecture.
def distance(v1, v2):
    distVector = v1-v2
    return np.dot(distVector, distVector)**0.5

class rodState(Enum):
    REST = 1
    LOAD = 2
    CASTED = 3
    PULL = 4

class Rod():

    def __init__(self, catPos, name):
        self.name = name
        self.hook = None
        self.state = rodState.REST
        if self.name == 'Basic Rod':
            self.fishingRodLength = 110
            self.pullSpeed = 10
        elif self.name == 'Good Rod':
            self.fishingRodLength = 150
            self.pullSpeed = 20
        elif self.name == 'Power Rod':
            self.fishingRodLength = 200
            self.pullSpeed = 30
        self.r = 10
        self.f = vec(0, 0)
        self.m = 10
        self.theta = 0 #radians
        self.loadDir = 'backwards'
        self.catPos = catPos
        self.pos = vec(self.catPos[0] + self.fishingRodLength, self.catPos[1])
        #used for euler integration
        self.v = vec(0,0) #This line is from physics TA mini-lecture.
        
    def cycleState(self):
        self.state = rodState((self.state.value % 4) + 1) #This line is from Google Search AI after I searched "How to switch Enum states".
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
        self.pos = vec(self.catPos[0] + self.fishingRodLength*math.cos(self.theta), self.catPos[1] - self.fishingRodLength*math.sin(self.theta))
  
    def castedHelper(self):
        if self.hook.theta <= -math.pi/2:
                self.cycleState()
        if self.theta > 0: #let the rod stop undulating
                self.theta -= math.pi/25
                self.pos = vec(self.catPos[0] + self.fishingRodLength*math.cos(self.theta), self.catPos[1] - self.fishingRodLength*math.sin(self.theta))

    def pullHelper(self):
        if self.hook.pos[1] <= self.catPos[1]:
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
        drawLine(float(x), float(y), int(self.catPos[0]), int(self.catPos[1]))
        if self.hook != None:
            drawLine(float(x), float(y), int(self.hook.pos[0]), int(self.hook.pos[1]))
    
    def __repr__(self):
        return(self.state.name)

class hookState(Enum):
    #I got the idea of using multiple states ("state control") to handle the 
    #changing behavior of the Hook, from Vincent Boling, Class of 2028, Physics.
    #He gave me some pseudocode of switching BETWEEN polar and kinematics equations 
    #as the rod changes states instead of using a universal real-time physics simulation 
    #like I was originally going to do. He also suggested I use Enum.
    #However, I added more states on top of his pseudocode such as 'REEL', 'PULL', implemented it completely on my own, and applied this method to other classes in an original way.
    PULL = 1
    CAST = 2
    REEL = 3

class Hook():

    def __init__(self, f, theta, loadDir, pos, fishingRodLength, catPos, pullSpeed):
        self.state = hookState.CAST
        self.r = 10
        self.m = 10
        self.f = f
        self.theta = -math.pi/10 #radians
        self.loadDir = loadDir
        self.catPos = catPos
        self.pos = pos
        self.fishingRodLength = fishingRodLength
        self.pullSpeed = pullSpeed
        
        #used for euler intergration
        self.v = vec(0,0) 
        
    def cycleState(self):
        self.state = hookState((self.state.value % 3) + 1)
        return self.state
    
    def pullHelper(self):
        if self.pos[1] >= self.catPos[1]:
                self.pos -= vec(0, self.pullSpeed)
    
    def castHelper(self):
        if self.pos[1] > 650:
            self.cycleState()
        a = self.f / self.m
        
        self.v[0] = math.pi*self.fishingRodLength/25/DT
        self.v = self.v + a * DT
        self.pos = self.pos + (self.v * DT)
        self.f = vec(0,0)

    def reelHelper(self):
        if self.theta <= -math.pi/2:
            self.cycleState()

        rodPos = (self.catPos[0] + self.fishingRodLength, self.catPos[1])
        reelRadius = distance(rodPos, self.pos)
        if self.theta > -math.pi/2:
            self.theta -= math.pi/150
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
    def __init__(self, pos):
        self.state = fishState.IDLE
        self.pos = pos
        self.theta = 0 #degrees
        self.size = 20
        self.theta = 0
        self.species = "Bluefin"
        self.value = 50

    def cycleState(self):
        self.state = fishState((self.state.value % 3) + 1)
        return self.state
    
    def moveHelper(self):
        if self.state == fishState.IDLE:
            if self.pos[0] < 650:
                self.theta += random.random()*random.randint(0, 1) #ensures fish do not run into land
            else:
                self.theta += random.random()*random.randint(-1, 1)
            self.pos += vec(int(2*math.cos(self.theta)), 0)
        #elif self.state == fishState.AGITATED:
        #    pass
            #move towards bait
        elif self.state == fishState.CAUGHT:
            pass

    def eulerUpdate(self):
        self.moveHelper()

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawImage('kenney_fishPack/PNG/Default size/fishTile_077.png', float(x), float(y), align = 'center')
        #drawCircle(float(x), float(y), self.size, fill = 'orange')


class mustardFish(Fish):
    def __init__(self, pos):
        super().__init__(pos)
        self.state = fishState.IDLE
        self.pos = pos
        self.theta = 0 #degrees
        self.size = 40
        self.theta = 0
        self.species = "Mustardfish"
        self.value = 400

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawImage('kenney_fishPack/PNG/Default size/fishTile_081.png', float(x), float(y), align = 'center', width = 125, height = 125)
        #drawCircle(float(x), float(y), self.size, fill = 'yellow')

class Quest:
    def __init__(self, species, amount, text):
        self.species = species
        self.amount = 0
        self.amountNeeded = amount
        self.text = text
    
    def isComplete(self):
        if self.amount == self.amountNeeded:
            return True
        else:
            return False

def onAppStart(app):
    app.width, app.height = 1440, 900
    app.paused = False
    app.catPos = vec(500, 500) 
    app.rod = Rod(app.catPos, 'Basic Rod')
    app.stepsPerSecond = 60
    #Leveling System
    app.money = 0
    app.exp = 0
    app.level = 0
    app.levelExpNeeded = 200
    #Fish System
    app.fish = []
    app.caughtFish = None
    app.pastFish = set()
    app.species = [Fish(vec(1100, 700)), mustardFish(vec(1100, 700))]
    app.smallFish = ["Bluefin"]
    app.mediumFish = ["Mustardfish"]
    #Menu System
    app.startMenu = False
    app.shopMenu = False
    app.backButton = False
    #app.journalMenu = False
    #app.tutorial1 = False
    app.quests = [Quest('Mustardfish', 1, 'Catch One Mustardfish!')]
    app.currentQuest = None
    #Drawing land / ocean / seafloor using Multiple Boards
    app.land = drawBoard('kenney_fishPack/PNG/Default size/fishTile_036.png', 7, 12, 0, 550, 600, 350)
    app.ocean = drawBoard('kenney_fishPack/PNG/Default size/fishTile_089.png', 5, 17, 600, 650, 850, 250)
    #Temporary Messages
    app.lvl1Message = False
    app.questCompletionMessage = False
    app.movableObjects = [app.rod]
    app.boatMode = False
    

class drawBoard(): #Credit: CMU CS Academy 2D Board Implementation
    def __init__(self, image, rows, cols, boardLeft, boardTop, boardWidth, boardHeight):
        self.image = image
        self.rows = rows
        self.cols = cols
        self.boardLeft = boardLeft
        self.boardTop = boardTop
        self.boardWidth = boardWidth
        self.boardHeight = boardHeight

    def getCellSize(self):
        cellWidth = self.boardWidth / self.cols
        cellHeight = self.boardHeight / self.rows
        return (cellWidth, cellHeight)

    def getCellLeftTop(self, row, col):
        cellWidth, cellHeight = self.getCellSize()
        cellLeft = self.boardLeft + col * cellWidth
        cellTop = self.boardTop + row * cellHeight
        return (cellLeft, cellTop)

    def drawCell(self, row, col): 
        cellLeft, cellTop = self.getCellLeftTop(row, col)
        cellWidth, cellHeight = self.getCellSize()
        drawImage(f'{self.image}', cellLeft, cellTop, width = cellWidth, height = cellHeight)
    
    def drawBoard(self): 
        for row in range(self.rows):
            for col in range(self.cols):
                self.drawCell(row, col)

    def draw(self):
        self.drawBoard()
    

def fishAdder(app):
    if len(app.fish) < 3:
        if random.randint(0, 60) == 0:
            pos = vec(random.randint(900,1200), random.randint(700,800))
            if random.randint(0,1) == 0:
                app.fish.append(Fish(pos))
            else:
                app.fish.append(mustardFish(pos))

def onStep(app):
    if app.paused: return
    app.rod.eulerUpdate()
    if app.rod.hook != None:
        app.rod.hook.eulerUpdate()

    #Fish Respawn
    fishAdder(app)

    #Reset app.rod's hook object after you pull the Fish in
    if app.rod.state == rodState.REST and app.rod.hook != None: 
            print('meow')
            app.rod.hook = None

    #Fish Catching
    for fish in app.fish:
        fish.eulerUpdate()
        if app.rod.hook != None and distance(app.rod.hook.pos, fish.pos) < 100 and app.caughtFish == None: #For catching a fish
            fish.state = fishState.CAUGHT
            app.caughtFish = fish
        if fish.state == fishState.CAUGHT and app.rod.hook != None:
            fish.pos = app.rod.hook.pos
        if fish.state == fishState.CAUGHT and (app.rod.state == rodState.LOAD) and app.caughtFish != None: #For throwing a fish
            fish.pos = app.rod.pos
    
    #Leveling System
    if app.exp >= app.levelExpNeeded:
        app.exp -= app.levelExpNeeded
        app.level += 1
        app.levelExpNeeded += 100 * app.level
        if app.level == 1:
            app.lvl1Message = True
    
    #Quest Logic
    if app.currentQuest != None:
        if app.caughtFish != None and app.caughtFish.species == app.currentQuest.species and app.rod.state == rodState.REST:
            app.currentQuest.amount += 1
        if Quest.isComplete(app.currentQuest):
            app.questCompletionMessage = True
            app.currentQuest = None
    
def onKeyPress(app, key):
    app.lvl1Message = False
    app.questCompletionMessage = False

    if 'space' in key:
        if app.caughtFish != None:
            return
        app.rod.cycleState()
        if app.rod.state == rodState.CASTED: #Create a new hook object when you cast your rod
            if app.rod.hook == None:
                app.rod.hook = Hook(app.rod.f, app.rod.theta, app.rod.loadDir, app.rod.pos, app.rod.fishingRodLength, app.catPos, app.rod.pullSpeed)
                app.moveableObjects.append(app.rod.hook)
    if 's' in key: #Selling Fish
        if app.currentQuest != None:
            print(app.currentQuest.text, app.currentQuest.amount)
        if app.caughtFish != None and app.rod.hook == None:
            for fish in app.fish:
                if fish.state == fishState.CAUGHT:
                    app.money += fish.value
                    app.fish.remove(fish)
                    if app.caughtFish.species not in app.pastFish:
                        app.pastFish.add(app.caughtFish.species)
                        if app.caughtFish.species in app.smallFish: #Unique fish EXP bonus
                            app.exp += 100
                        elif app.caughtFish.species in app.mediumFish:
                            app.exp += 300
                        else:
                            app.exp += 1000
                    print(app.caughtFish, app.pastFish)
                    app.exp += 50
                    app.caughtFish = None
    if 'right' in key:
        for object in app.moveableObjects:
            object.pos += vec(10,0)
    if 'left' in key:
        for object in app.moveableObjects:
            object.pos += vec(-10,0)
                    

def onMousePress(app, mouseX, mouseY):
    app.lvl1Message = False
    app.questCompletedMessage = False

    #Menu buttons
    if app.startMenu == True:
        if 480 < mouseX < 960 and 333 < mouseY < 513:
            app.startMenu = False
    if app.backButton == True:
        if 1220 < mouseX < 1420 and 610 < mouseY < 790:
            app.shopMenu = False
            app.backButton = False
    if app.shopMenu == True:
        if 40 < mouseX < 280 and 10 < mouseY < 330:
            app.rod = Rod(app.catPos, 'Basic Rod')
        if 295 < mouseX < 535 and 10 < mouseY < 330:
            app.rod = Rod(app.catPos, 'Good Rod')
        if 540 < mouseX < 790 and 10 < mouseY < 330:
            app.rod = Rod(app.catPos, 'Power Rod')

    #Quest Button
    if app.level >= 1 and app.currentQuest == None and len(app.quests) != 0: 
        if 1220 < mouseX < 1420 and 120 < mouseY < 300:
            app.currentQuest = app.quests.pop()

def onMouseRelease(app, mouseX, mouseY):
    if app.level >= 1 and app.shopMenu == False:
        if 40 < mouseX < 240 and 20 < mouseY < 200:
            app.shopMenu = True
            app.backButton = True

def redrawAll(app):
    #Draw Backgrounds
    app.land.draw()
    app.ocean.draw()
    #Draw Cat
    catX, catY = app.catPos[0], app.catPos[1]
    drawImage('PC Computer - Stardew Valley - Cat White (1).png', float(catX), float(catY), align = 'center', width = 100, height = 100)
    #drawRect(float(catX), float(catY), 100, 100, align = 'center')
    #Draw Hook and Rod
    app.rod.draw()
    if app.rod.hook != None:
        app.rod.hook.draw()
    for fish in app.fish:
        fish.draw()
    #Draw Money and Levels
    drawLabel(f'${app.money}', 1300, 50, size = 60, font='caveat')
    #drawLabel(f'exp is {app.exp}', 1300, 700, size = 40, font = 'caveat')
    drawLabel(f'Lvl.{app.level}', 550, 820, size = 40, font = 'caveat')
    if app.exp < app.levelExpNeeded and app.exp != 0:
        drawRect(620, 800, 800 // (app.levelExpNeeded // app.exp), 40, fill = 'lightYellow') #exp bar goes from 0-800 pixels
    else:
        drawRect(620, 800, 1, 40, fill = 'lightYellow') #exp bar goes from 0-800 pixels
    drawRect(620, 800, 800, 40, fill = None, border = 'paleGoldenrod', borderWidth = 6)
    #Draw Caught Fish Info
    if app.caughtFish != None and app.rod.state == rodState.REST:
        drawLabel(f'{app.caughtFish.species}', app.width//2, app.height//2 - 150, size = 100)
        drawLabel(f'Worth ${app.caughtFish.value}', app.width//2, app.height//2 - 70, size = 50)
        drawLabel(f'Press S to sell', app.width//2, app.height//2, size = 20)

    #Quests
    if app.level >= 1 and app.currentQuest == None and app.questCompletionMessage == False:
        drawRect(1220, 120, 200, 180, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawLabel('New Quest', 1320, 200, size = 40, align = 'center', font='caveat')
    if app.currentQuest != None:
        drawLabel(f'{app.currentQuest.text} {app.currentQuest.amount}/{app.currentQuest.amountNeeded}', app.width//2 + 680, app.height//2 + 340, align = 'right-top', size = 25)
    
    
    #Temporary Level-Up Messages
    if app.lvl1Message == True and app.caughtFish == None:
        drawLabel('Unlocked Rod Shop!', app.width//2, app.height//2 - 70, size = 50, font = 'caveat')
    if app.questCompletionMessage == True and app.caughtFish == None:
        drawLabel('Quest Completed!', app.width//2, app.height//2 - 70, size = 50, font = 'caveat')
    #Buttons
    if app.level >= 1 and app.shopMenu == False:
        drawRect(40, 20, 200, 180, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawLabel('Rods', 140, 100, size = 60, align = 'center', font = 'caveat')
    if app.backButton == True:
        drawRect(1220, 610, 200, 180, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawLabel('Back', 1320, 700, size = 40, align = 'center', font='caveat')

    #Draw Menus
    if app.startMenu == True:
        drawRect(app.width//2, app.height//2, 480, 180, align = 'center', fill = 'steelBlue')
        drawLabel('Start Game', app.width//2, app.height//2, size = 50, align = 'center', font = 'cinzel')
        return
    if app.shopMenu == True:
        #Fishing Rod Upgrades
        drawRect(40, 10, 240, 320, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawRect(295, 10, 240, 320, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawRect(550, 10, 240, 320, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        if app.rod.name == 'Basic Rod':
            drawRect(40, 10, 240, 320, fill = 'lightYellow')
        elif app.rod.name == 'Good Rod':
            drawRect(295, 10, 240, 320, fill = 'lightYellow')
        elif app.rod.name == 'Power Rod':
            drawRect(550, 10, 240, 320, fill = 'lightYellow')
        drawLabel('Basic Rod', 60, 30, size = 30, align = 'left-top')
        drawLabel('Good Rod', 315, 30, size = 30, align = 'left-top')
        drawLabel('Power Rod', 570, 30, size = 30, align = 'left-top')
        #image
        drawRect(60, 70, 200, 120, fill = 'darkKhaki')
        drawRect(315, 70, 200, 120, fill = 'darkKhaki')
        drawRect(570, 70, 200, 120, fill = 'darkKhaki')
        #power bars
        drawRect(100, 210, 160, 25, fill = 'darkKhaki')
        drawRect(100, 245, 160, 25, fill = 'darkKhaki')
        drawRect(100, 280, 160, 25, fill = 'darkKhaki')
        
        drawRect(355, 210, 160, 25, fill = 'darkKhaki')
        drawRect(355, 245, 160, 25, fill = 'darkKhaki')
        drawRect(355, 280, 160, 25, fill = 'darkKhaki')
        
        drawRect(610, 210, 160, 25, fill = 'darkKhaki')
        drawRect(610, 245, 160, 25, fill = 'darkKhaki')
        drawRect(610, 280, 160, 25, fill = 'darkKhaki')

        
    
        
    



def main():
    cmu_graphics.runApp()

main()


