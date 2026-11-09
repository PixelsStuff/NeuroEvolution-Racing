import pygame
import os
import random
import math
import neat
import time
from pathlib import Path
pygame.font.init()
WINDH = 9*100
WINDW = 16*100
STATFONT = pygame.font.SysFont('comicsans',30)
STATFONTBUTBIG = pygame.font.SysFont('comicsans',90)

currentdir = Path(__file__).parent.resolve()

carimglink = currentdir / 'CAR.png'
playerimg =pygame.transform.scale(pygame.image.load(carimglink),(128,128))
clock = pygame.time.Clock()
win = pygame.display.set_mode((WINDW,WINDH))
path = currentdir / 'TrackData.txt'
allobjects = []
startpos = (100,800,10)
endpos = (0,0,1)
showplayer = False
showrays = False
gen = 0
simulationacceleration = 0
timetonextframe = 0 

INITALENDBONUS = 400
ENDTAMPERRATE = 0.8
ENDBONUSTIME = 0.5
REDISWALL = True
configpath = currentdir / 'RacingsimNEATconfig.txt'
class Obj(pygame.sprite.Sprite):
     def __init__(self, x,y,rad,shape=1):
          super().__init__()
          self.PosX = x
          self.PosY = y
          self.rad = rad
          self.type = type
          self.shape = shape
     def draw(self,screen):
          if self.shape == 1:
               pygame.draw.circle(screen,(255,100,100),(self.PosX,self.PosY),self.rad)
          elif self.shape == 2:
               pygame.draw.rect(win,(255,100,100),(self.PosX-math.sqrt(self.rad**2/2),self.PosY-math.sqrt(self.rad**2/2),2*math.sqrt(self.rad**2/2),2*math.sqrt(self.rad**2/2)))
          else:
               pygame.draw.circle(screen,(50,255,50),(self.PosX,self.PosY),self.rad)
               pygame.draw.circle(win,(200,200,200),(self.PosX,self.PosY),(self.rad+1)//1.2)

def writetosave(path,objectlist):
    with open(path,'w') as f:
     f.write('')
    for thing in objectlist:
        with open(path,'a') as f:
             f.write(f'{thing.PosX},{thing.PosY},{thing.rad},{thing.shape} \n')

def interpretobjects(path):
    global allobjects
    global startpos
    global endpos
    with open(path,'r') as f:
         text = f.read()
    fullolist = text.split('\n')
    for thing in fullolist:
        if len(thing) > 0:
            aob = thing.split()[0].strip("[]'\" ").split(',')
            if int(aob[3]) <= 2:
                allobjects.append(Obj(int(aob[0]),int(aob[1]),int(aob[2]),int(aob[3])))
            elif int(aob[3]) ==3:
                startpos = (int(aob[0]),int(aob[1]),int(aob[2]))
            if int(aob[3]) == 4:
                allobjects.append(Obj(int(aob[0]),int(aob[1]),int(aob[2]),int(aob[3])))
                endpos = (int(aob[0]),int(aob[1]),int(aob[2]))

class Player:
    def __init__(self,x,y,id=random.randint(0,100000)):
        self.x = x
        self.y = y
        self.img = playerimg
        self.angle = 0
        self.vel = 0
        self.accel = 0.25
        self.halffactor = 10
        self.action = 0
        self.sensorres = [(500,0,0),(500,0,0),(500,0,0),(500,0,0),(500,0,0)]
        self.greensensors = [(500,0,0),(500,0,0),(500,0,0),(500,0,0),(500,0,0)]
        self.id = id

        self.disttoend = 500
    def accelerate(self):
        self.action = 1
        if self.vel > self.halffactor:
            self.vel += self.accel / math.log(self.vel,self.halffactor)
        else:
             self.vel += self.accel
    def turnright(self):
         self.angle -= 5
         if self.angle < 0:
          self.angle+= 360
    def turnleft(self):
         self.angle += 5
         if self.angle < 0:
          self.angle+= 360

    def draw(self,win):
            rotatedimg  = pygame.transform.rotate(self.img,self.angle-90)
            newrect = rotatedimg.get_rect(center=self.img.get_rect(center=(self.x, self.y)).center)
            win.blit(rotatedimg,newrect)

def drawwindow(win,players):
    global showrays
    global allobjects
    global playercontrolled
    win.fill('white')
    for thing in allobjects:
        thing.draw(win)
    distcalcpos = (0,0,0)
    smallestthingy = 999
    for player in players:
             player.draw(win)
    if showplayer:
        playercontrolled.draw(win)
        if showrays:
             for point in playercontrolled.sensorres:
                pygame.draw.circle(win,(130,130,230),(point[1],point[2]),10)
             for point in playercontrolled.greensensors:
                pygame.draw.circle(win,(130,230,130),(point[1],point[2]),10)  
    if showrays:
        for player in players:
             for point in player.sensorres:
                  pygame.draw.circle(win,(130,130,230),(point[1],point[2]),10)
    if not simulationacceleration:
        fps = clock.get_fps()
        text = STATFONT.render(f"FPS: {fps:.1f}", True, (0, 0, 0))
    else:
        if simulationacceleration == 1:
            text = STATFONT.render(f"Acceleration Enabled", True, (0, 0, 0))
        else:
            text = STATFONT.render(f"Hyper-Accel Enabled", True, (0, 0, 0))
    win.blit(text, (10, 10))
    text = STATFONT.render(f"Generation: {gen:.1f}", True, (0, 0, 0))
    win.blit(text, (9, 30))
    
    pygame.display.update()

def drawgenscreen(win):
        win.fill('white')
        fps = clock.get_fps()
        text = STATFONT.render(f"FPS: {fps:.1f}", True, (0, 0, 0))
        win.blit(text, (10, 10))
        text = STATFONTBUTBIG.render(f"Hyper-Acceleration Enabled", True, (0, 0, 0))
        win.blit(text, (WINDW/2-400, WINDH/2-60))
        text = STATFONTBUTBIG.render(f"Generation: {gen:.1f}", True, (0, 0, 0))
        win.blit(text, (WINDW/2-400, WINDH/2))
        pygame.display.update()
     
def sensordetectdistance(xcori,ycori,angle,oblist):
      distcalcpos = (500,xcori+math.cos(angle/180*math.pi),ycori-math.sin(angle/180*math.pi))
      smallestdist = 500
      for objectl in oblist:
            if objectl.shape != 4:
                result = pointdetectdistance(xcori,ycori,objectl.PosX,objectl.PosY,objectl.rad,angle)
                if 0 < result[0] < smallestdist:
                    smallestdist = result[0]
                    distcalcpos = result
      return distcalcpos

def pointdetectdistance(xcori,ycori,xcorf,ycorf,rad,angle):
      dist = 0
      xcor = xcori
      ycor = ycori #The intersection of a circle and a ray seems to turns out to be the quadratic formula where a is length of a unit of direction vector, b compares it to the circles center, and c gets the outer bounds of the circle. This one is harder to explain. I am not skilled enough to derive that one without help.
      #math.cos((angle)/180*math.pi)
      a = 1 #math.cos((angle)/180*math.pi)**2 + math.sin((angle)/180*math.pi)**2 <--- just euqals 1
      b = 2 * ((xcori-xcorf) * (math.cos((angle)/180*math.pi)) + ((ycori-ycorf) * (-math.sin((angle)/180*math.pi))))
      c = (xcori-xcorf)**2 + (ycori-ycorf)**2 - rad**2
      if b**2 - 4*a*c < 0:
        return 500,0,0
      quadraticpointfirst = (-b + math.sqrt(b**2 - 4*a*c))/ (2*a) #This is just the quadratic formula which is pretty cool
      quadraticpointsecond = (-b - math.sqrt(b**2 - 4*a*c))/ (2*a)
      dist = min([quadraticpointfirst,quadraticpointsecond,500])
      xcor = xcori + dist * math.cos((angle)/180*math.pi)
      ycor = ycori - dist * math.sin((angle)/180*math.pi)

      return round(dist,2),round(xcor,2),round(ycor,2)
      
interpretobjects(path)

def main(genomes,config):
     global showplayer
     global simulationacceleration
     global playercontrolled
     global gen
     gen += 1
     nets = []
     cars = []
     ge = []
     quota = 0
     endbounty = INITALENDBONUS
     countdown = -1
     carids = 0
     woncarids = []
     global timetonextframe
     for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        cars.append(Player(startpos[0]+random.randint(-startpos[2],startpos[2]),startpos[1]+random.randint(-startpos[2],startpos[2]),carids))
        carids += 1
        g.fitness = 0
        ge.append(g)

     timepassed = 0
     playercontrolled = Player(startpos[0]+random.randint(-startpos[2],startpos[2]),startpos[1]+random.randint(-startpos[2],startpos[2]))
     running = True

     while running:
        tt = time.time()
        
        if simulationacceleration ==0:
            clock.tick(30)
        timepassed += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                     simulationacceleration += 1
                     simulationacceleration = simulationacceleration %3
                     print('simulation acceleration:',simulationacceleration)
                if event.key== pygame.K_p:
                     showplayer = not showplayer
        for count,car in enumerate(cars):
            amcolliding = False
            for thing in allobjects:
                if math.sqrt((car.x-thing.PosX)**2 + (car.y-thing.PosY)**2) < thing.rad:
                     amcolliding = True
                     if thing.shape == 4 and car.id not in woncarids:
                          ge[count].fitness += endbounty
                          endbounty *= 0.8
                          woncarids.append(car.id)
                          if countdown == -1:
                            countdown = ENDBONUSTIME * 30
                          break
                     else:
                          ge[count].fitness -= 700/(30*20)
            if simulationacceleration != 3 or (simulationacceleration==3 and timepassed %2 ==0 or timepassed < 2):
                if amcolliding:
                    car.sensorres = [(0,car.x,car.y)] * 5
                else:
                    car.sensorres =[]
                    car.greensensors = []
                    for pos in [0,15,45,-15,-45]:
                        car.sensorres.append(sensordetectdistance(car.x,car.y,car.angle+pos,oblist=allobjects))
                        car.greensensors.append(pointdetectdistance(car.x,car.y,endpos[0],endpos[1],endpos[2],car.angle+pos))


            car.disttoend = math.sqrt((car.x-endpos[0])**2 + (car.y-endpos[1])**2)-endpos[2]
            car.action = 0
            output = nets[count].activate((car.x, car.y,car.angle,car.disttoend,car.sensorres[0][0]/500,
                                           car.sensorres[1][0]/500,car.sensorres[2][0]/500,car.sensorres[3][0]/500,car.sensorres[4][0]/500,car.greensensors[0][0]/500,car.greensensors[1][0]/500,car.greensensors[2][0]/500,car.greensensors[3][0]/500,car.greensensors[4][0])) #maybe add 
            if output[0] > 0.5:
                car.accelerate()
            if output[1] > 0.5:
                car.turnright()
            if output[2] > 0.5:
                car.turnleft()

            if amcolliding:
                    if REDISWALL:
                        car.vel = -0
                        car.x -= 5 * math.cos(car.angle/180*math.pi)
                        car.y -= 5 * -math.sin(car.angle/180*math.pi)
                    else:
                        car.vel = max(1,car.vel*0.8)
                    
            if car.vel > car.halffactor:
                    car.vel += car.accel / math.log(car.vel,car.halffactor)
            else:
                 car.vel += car.accel
            car.x += car.vel * math.cos(car.angle/180*math.pi)
            car.y += car.vel * -math.sin(car.angle/180*math.pi)

            if car.x < 0:
                 car.x = 0
                 car.vel *= 0.95
            elif car.x > WINDW:
                car.x = WINDW
                car.vel *= 0.95
            if car.y > WINDH:
                 car.y = WINDH
                 car.vel *= 0.95
            if car.y < 0:
                 car.y = 0
                 car.vel *= 0.95



            if car.action != 1:
                if car.vel > 0.1:
                    car.vel *= 0.9
                if car.vel <0:
                    car.vel = 0

        playercontrolled.action = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
                    playercontrolled.accelerate()
        if keys[pygame.K_LEFT]:
                    playercontrolled.turnleft()
        if keys[pygame.K_RIGHT]:
                    playercontrolled.turnright()
        elif keys[pygame.K_DOWN]:
                     playercontrolled.vel -= playercontrolled.accel/2
        amcolliding = False
        for thing in allobjects:
            if math.sqrt((playercontrolled.x-thing.PosX)**2 + (playercontrolled.y-thing.PosY)**2) < thing.rad:
                amcolliding = True
        if amcolliding:
                    playercontrolled.vel = max(1,playercontrolled.vel*0.8)
                    playercontrolled.vel += playercontrolled.accel
        if not (REDISWALL and amcolliding):
            playercontrolled.x += playercontrolled.vel * math.cos(playercontrolled.angle/180*math.pi)
            playercontrolled.y += playercontrolled.vel * -math.sin(playercontrolled.angle/180*math.pi)
        if playercontrolled.action != 1:
            if playercontrolled.vel > 0.1:
                playercontrolled.vel *= 0.9
            if playercontrolled.vel <0:
                playercontrolled.vel = 0
        if showplayer and showrays:
            if amcolliding:
                 playercontrolled.sensorres = [(0,playercontrolled.x,playercontrolled.y)] * 5
            else:
                playercontrolled.sensorres =[]
                playercontrolled.greensensors = []
                for pos in [0,15,45,-15,-45]:
                 playercontrolled.sensorres.append(sensordetectdistance(playercontrolled.x,playercontrolled.y,playercontrolled.angle+pos,oblist=allobjects))
                 playercontrolled.greensensors.append(pointdetectdistance(playercontrolled.x,playercontrolled.y,endpos[0],endpos[1],endpos[2],playercontrolled.angle+pos))
        if 30 * 20 == timepassed or len(cars) == 0 or  (-1<countdown<1):
             for count,car in enumerate(cars): #SCORING FOR OTHER CARS
                ge[count].fitness += (1000 - math.sqrt((car.x - endpos[0])**2 + (car.y - endpos[1])**2)) - 200*(timepassed/(30*20))
             running = False
        if countdown > -1:
             countdown -=1


        if simulationacceleration !=0:
             if simulationacceleration == 2:
                    if time.time() > timetonextframe:
                         timetonextframe = time.time() + 0.1
                         drawgenscreen(win=win)
             else:
                  if time.time() > timetonextframe:
                    timetonextframe = time.time() + 1/30
                    drawwindow(win=win,players=cars)
        else:
            drawwindow(win=win,players=cars)
        
        #if timepassed % 30 == 0:
        #    print('speed:',0.33/(time.time()-tt))
       # print('ittime',time.time()-tt)

def run(configpath=configpath):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,configpath)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main,5000) 
if __name__ == '__main__':
    run()

