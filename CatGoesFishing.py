import numpy as np 
from enum import Enum
import math
from cmu_graphics import *
from PIL import Image
import random

#This function is from physics TA mini-lecture.
def vec(x, y):
    return np.array([x, y])

G = 10000
FPS = 60
DT = 1/60
#https://opengameart.org/content/fish-pack-0
bckImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/624b4055-7b77-4099-8113-3c72abe73559.png')) #https://www.freepik.com/free-vector/natural-environment-lanscape-scene_5597221.htm#fromView=keyword&page=1&position=0&uuid=20cf8488-9d10-4e9d-8637-27addb17cb57
blueFinImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/kenney_fishPack/PNG/Default size/fishTile_077.png'))
boatImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/simple-historic-boat-illustration-45dd9d.png')) #https://www.vexels.com/png-svg/preview/206225/simple-historic-boat-illustration
mustardFishImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/kenney_fishPack/PNG/Default size/fishTile_081.png'))
landImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/kenney_fishPack/PNG/Default size/fishTile_036.png'))
oceanImage1 = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/kenney_fishPack/PNG/Default size/fishTile_088.png'))
oceanImage2 = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/kenney_fishPack/PNG/Default size/fishTile_089.png'))
catImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/PC Computer - Stardew Valley - Cat White (1).png')) #opengameart.org
skyImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/SL-031821-41530-04-min.jpg')) #https://www.vecteezy.com/vector-art/4939146-sky-with-cloud-cartoon-background-vector-flat-style
rockImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/kenney_fishPack/PNG/Default size/fishTile_084.png'))
wallpaperImage = CMUImage(Image.open('/Users/kyleluo/Documents/GitHub/CatGoesFishing/luanne-boudier-cat-fishing-art.jpg')) #https://www.artstation.com/artwork/5vKBYP

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
        drawCircle(float(x), float(y), self.r, fill = 'darkSlateGray')
        drawLine(float(x), float(y), int(self.catPos[0]), int(self.catPos[1]), fill= 'saddleBrown', lineWidth = 3)
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

    def __repr__(self):
        return(self.state.name)

class fishState(Enum):
    IDLE = 1
    AGITATED = 2
    CAUGHT = 3

class Fish():
    def __init__(self, pos):
        self.state = fishState.IDLE
        self.hookPos = None
        self.pos = pos
        self.theta = 0 #degrees
        self.rotateAngle = 0
        self.size = 20
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
        elif self.state == fishState.AGITATED:
            adjacent = abs(self.pos[0] - self.hookPos[0])
            opposite = abs(self.pos[1] - self.hookPos[1])
            self.rotateAngle += -math.degrees(math.atan(opposite/adjacent))//10
            r = distance(self.pos, self.hookPos)//20
            self.pos += vec(int(r*math.cos(self.rotateAngle)), int(r*math.sin(self.rotateAngle)))
        elif self.state == fishState.CAUGHT:
            self.rotateAngle = -90

    def eulerUpdate(self):
        self.moveHelper()

    def draw(self):
        x, y = self.pos[0], self.pos[1]
        drawImage(blueFinImage, float(x), float(y), align = 'center', rotateAngle = self.rotateAngle)


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
        drawImage(mustardFishImage, float(x), float(y), align = 'center', width = 125, height = 125, rotateAngle = self.rotateAngle)

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

class Boat:
    def __init__(self, name):
        self.pos = vec(900, 480)
    
    def draw(self):
        x, y = self.pos[0], self.pos[1]
        #https://www.vexels.com/png-svg/preview/206225/simple-historic-boat-illustration
        drawImage(boatImage, float(x), float(y), align = 'center')

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
    app.largeFish = []
    #Menu System
    app.startMenu = True
    app.shopMenu = False
    app.backButton = False
    #app.journalMenu = False
    #app.tutorial1 = False
    app.quests = [Quest('Mustardfish', 1, 'Catch One Mustardfish!')]
    app.currentQuest = None
    #Drawing land / ocean / seafloor using Multiple Boards
    app.land = drawBoard(landImage, 7, 12, 0, 550, 600, 350)
    app.ocean = drawBoard(oceanImage2, 5, 40, 600, 650, 2000, 250)
    app.bckX = -200
    app.skyX = -100
    app.rockX = 100
    #Temporary Messages
    app.lvl0Message = True
    app.lvl1Message = False
    app.lvl3Message = False
    app.questCompletionMessage = False
    app.boatMode = False
    app.boat = None
    

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
        drawImage(self.image, cellLeft, cellTop, width = cellWidth, height = cellHeight)
    
    def drawBoard(self): 
        for row in range(self.rows):
            for col in range(self.cols):
                self.drawCell(row, col)

    def draw(self):
        self.drawBoard()
    

def fishAdder(app):
    
    if app.level < 3:
        spawnWidth = 1200
        totalFish = 3
    else:
        spawnWidth = 1500
        totalFish = 6
    if len(app.fish) < totalFish:
        if random.randint(0, 60) == 0:
            pos = vec(random.randint(900,spawnWidth), random.randint(700,800))
            if random.randint(0,1) == 0:
                app.fish.append(Fish(pos))
            else:
                app.fish.append(mustardFish(pos))

def onStep(app):
    print(app.catPos)
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
        if app.rod.hook != None:
            fish.hookPos = app.rod.hook.pos
            if distance(app.rod.hook.pos, fish.pos) < 150 and app.caughtFish == None and fish.state == fishState.IDLE:
                fish.state = fishState.AGITATED
            if (app.caughtFish != None or distance(app.rod.hook.pos, fish.pos) > 150)and fish.state == fishState.AGITATED:
                fish.state = fishState.IDLE
                fish.rotateAngle = 0
            if distance(app.rod.hook.pos, fish.pos) < 100 and app.caughtFish == None: #For catching a fish
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
        if app.level == 3:
            app.lvl3Message = True
    
    #Quest Logic
    if app.currentQuest != None:
        if app.caughtFish != None and app.caughtFish.species == app.currentQuest.species and app.rod.state == rodState.REST:
            app.currentQuest.amount += 1
        if Quest.isComplete(app.currentQuest):
            app.questCompletionMessage = True
            app.exp += app.levelExpNeeded
            app.currentQuest = None
    
    #Boating Mode Centering Of Camera
    if app.boat != None and app.boatMode == False:
        centerValue = -100
        app.land.boardLeft += centerValue
        app.ocean.boardLeft += centerValue
        app.skyX += centerValue
        app.bckX += centerValue
        app.rockX += centerValue
        for fish in app.fish:
            fish.pos += vec(centerValue, 0)
        app.boatMode = True
    
    #Start Boat Mode
    if app.boatMode == True and app.boat != None and app.rod.state == rodState.REST:
        app.catPos = app.boat.pos + vec(-50, 50)
        #Make sure the rod knows where the cat is
        app.rod.catPos = app.catPos
        app.rod.pos = vec(app.catPos[0] + app.rod.fishingRodLength, app.catPos[1])
    
    #End Boat Mode
    if app.boat != None and app.land.boardLeft >= 0:
        app.catPos = vec(500, 500)
        centerValue = -100
        app.land.boardLeft = 0
        app.ocean.boardLeft = 600
        app.rod.catPos = app.catPos
        app.rod.pos = vec(app.catPos[0] + app.rod.fishingRodLength, app.catPos[1])
        app.boatMode = False
        app.boat = None
    

def onKeyPress(app, key):
    if 'l' in key:
        app.exp += 100

    if app.caughtFish == None:
        app.lvl0Message = False
        app.lvl1Message = False
        app.lvl3Message = False
        app.questCompletionMessage = False

    if 'space' in key:
        if app.caughtFish != None:
            return
        app.rod.cycleState()
        if app.rod.state == rodState.CASTED: #Create a new hook object when you cast your rod
            if app.rod.hook == None:
                app.rod.hook = Hook(app.rod.f, app.rod.theta, app.rod.loadDir, app.rod.pos, app.rod.fishingRodLength, app.catPos, app.rod.pullSpeed)
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
                        elif app.caughtFish.species in app.largeFish:
                            app.exp += 1000
                    app.exp += 50
                    app.caughtFish = None

def onKeyHold(app, key):
    if app.boatMode == True:
        if 'right' in key or 'left' in key:

            if 'right' in key:
                scroll = -10
            if 'left' in key:
                scroll = 10

            if (not('left' in key and app.catPos[0] == 500)) and not(app.land.boardLeft == -760 and ('right' in key)) and (app.rod.state == rodState.REST): #Don't go off the edge, and don't move when you're fishing
                app.skyX += scroll
                app.bckX += scroll
                app.rockX += scroll
                app.catPos = app.catPos + vec(scroll, 0)
                app.land.boardLeft += scroll
                app.ocean.boardLeft += scroll
                app.rod.pos += vec(scroll, 0)
                for fish in app.fish:
                    fish.pos += vec(scroll, 0)
        
        
def onMousePress(app, mouseX, mouseY):
    if app.caughtFish == None:
        app.lvl0Message = False
        app.lvl1Message = False
        app.lvl3Message = False
        app.questCompletedMessage = False

    #Menu buttons
    if app.startMenu == True:
        if 600 < mouseX < 840 and 678 < mouseY < 768:
            app.startMenu = False
            app.lvl0Message = True
    if app.backButton == True and app.boatMode != True:
        if 1220 < mouseX < 1420 and 610 < mouseY < 790:
            app.shopMenu = False
            app.backButton = False
    if app.shopMenu == True and app.boatMode != True:
        if 40 < mouseX < 280 and 10 < mouseY < 330:
            app.rod = Rod(app.catPos, 'Basic Rod')
        if 295 < mouseX < 535 and 10 < mouseY < 330:
            app.rod = Rod(app.catPos, 'Good Rod')
        if 540 < mouseX < 790 and 10 < mouseY < 330:
            app.rod = Rod(app.catPos, 'Power Rod')
    if app.level >= 3 and app.boatMode != True and app.shopMenu != True:
        if 260 < mouseX < 460 and 20 < mouseY < 200:
            app.rod.state = rodState.REST
            app.boat = Boat('Basic Boat')
    
    #Quest Button
    if app.level >= 1 and app.currentQuest == None and len(app.quests) != 0 and app.boatMode != True: 
        if 1220 < mouseX < 1420 and 120 < mouseY < 300:
            app.currentQuest = app.quests.pop()

def onMouseRelease(app, mouseX, mouseY):
    if app.level >= 1 and app.shopMenu == False:
        if 40 < mouseX < 240 and 20 < mouseY < 200:
            app.shopMenu = True
            app.backButton = True

def redrawAll(app):
    if app.startMenu == True:
        drawImage(wallpaperImage, 0, 0)
        drawRect(app.width//2, app.height//2+300, 240, 90, align = 'center', fill = 'steelBlue')
        drawLabel('Start Game', app.width//2, app.height//2+300, size = 50, align = 'center', font = 'caveat')
        drawLabel('Welcome to Cat Goes Fishing!', app.width//2, app.height//2-300, size = 70, align = 'center', font = 'caveat')
        drawLabel('Start out on an island with a basic rod. Progress into a master fisher-cat scouring the sea', app.width//2, app.height//2-200, size = 30, align = 'center', font = 'caveat') #Opening message is taken directly from the offical game. https://cat-goes-fishing.fandom.com/wiki/Cat_Goes_Fishing_Wiki
        drawLabel('for the biggest and baddest fish. Each fish has unique behaviors that you will learn to exploit as you tailor', app.width//2, app.height//2-150, size = 30, align = 'center', font = 'caveat')
        drawLabel('your arsenal of fishing rods to suit your style of play. Mrrrow!', app.width//2, app.height//2-100, size = 30, align = 'center', font = 'caveat')
        return
    #Draw Backgrounds
    drawImage(skyImage, app.skyX, -600, width = 2333, height = 1333)
    drawImage(bckImage, app.bckX, 200, width = 2412, height = 570)
    app.land.draw()
    drawImage(rockImage, app.rockX, 485)
    app.ocean.draw()
    #Draw Cat
    catX, catY = app.catPos[0], app.catPos[1]
    drawImage(catImage, float(catX), float(catY), align = 'center', width = 100, height = 100)
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
    if app.level >= 1 and app.currentQuest == None and app.questCompletionMessage == False and len(app.quests) > 0 and app.boatMode != True:
        drawRect(1220, 120, 200, 180, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawLabel('New Quest', 1320, 200, size = 40, align = 'center', font='caveat')
    if app.currentQuest != None:
        drawLabel(f'{app.currentQuest.text} {app.currentQuest.amount}/{app.currentQuest.amountNeeded}', app.width//2 + 680, app.height//2 + 340, align = 'right-top', size = 25)
    
    #Temporary Level-Up Messages
    if app.lvl0Message == True:
        drawLabel('Press Space to Begin Fishing. Go Forth, Young Cat!', app.width//2, app.height//2 - 70, size = 40, font = 'caveat')
    if app.lvl1Message == True and app.caughtFish == None:
        drawLabel('Unlocked Rod Shop!', app.width//2, app.height//2 - 70, size = 50, font = 'caveat')
    if app.lvl3Message == True and app.caughtFish == None:
        drawLabel('Unlocked Boats!', app.width//2, app.height//2 - 70, size = 50, font = 'caveat')
    if app.questCompletionMessage == True and app.caughtFish == None and app.lvl3Message != True:
        drawLabel('Quest Completed!', app.width//2, app.height//2 - 70, size = 50, font = 'caveat')
    #Buttons
    if app.level >= 1 and app.shopMenu == False and app.boatMode != True:
        drawRect(40, 20, 200, 180, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawLabel('Rods', 140, 100, size = 60, align = 'center', font = 'caveat')
    if app.backButton == True and app.boatMode != True:
        drawRect(1220, 610, 200, 180, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawLabel('Back', 1320, 700, size = 40, align = 'center', font='caveat')
    if app.level >= 3 and app.boatMode != True and app.shopMenu != True:
        drawRect(260, 20, 200, 180, fill = gradient('lemonChiffon', 'paleGoldenrod', start = 'top'))
        drawLabel('Boat', 360, 100, size = 60, align = 'center', font = 'caveat')

    #Draw Menus
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

    if app.boatMode == True:
        app.boat.draw()

def main():
    cmu_graphics.runApp()

main()