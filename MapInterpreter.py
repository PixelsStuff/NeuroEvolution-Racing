import pygame
import random
import math
from pathlib import Path
currentdir = Path(__file__).parent.resolve()
path = currentdir / 'TrackData.txt'

width = 16*100 
height = 9*100
clock = pygame.time.Clock()
win = pygame.display.set_mode((width,height))

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
          elif self.shape == 4:
               pygame.draw.circle(screen,(50,255,50),(self.PosX,self.PosY),self.rad)
               pygame.draw.circle(win,(200,200,200),(self.PosX,self.PosY),(self.rad+1)//1.2)
          elif self.shape == 3:
               pygame.draw.circle(screen,(50,50,50),(self.PosX,self.PosY),self.rad)
               pygame.draw.circle(win,(200,200,200),(self.PosX,self.PosY),(self.rad+1)//1.2)



def writetosave(path,objectlist):
    with open(path,'w') as f:
     f.write('')
    for thing in objectlist:
        with open(path,'a') as f:
             f.write(f'{thing.PosX},{thing.PosY},{thing.rad},{thing.shape}\n')


running = True
pygame.init()
radius = 30
objects = []
selectedshape = 1
while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
               if event.button == 1: 
                    clickx,clicky = event.pos

                    if selectedshape == 3:
                        for thing in objects:
                            if thing.shape == 3:
                                objects.remove(thing)
                    elif selectedshape == 4:
                         for thing in objects:
                              if thing.shape == 4:
                                   objects.remove(thing)
                    objects.append(Obj(clickx,clicky,radius,selectedshape)) 



            elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_RIGHT:
                    selectedshape += 1
                    if selectedshape == 5:
                     selectedshape = 1
                    if selectedshape == 2:
                        selectedshape += 1
                    print(selectedshape)
               if event.key == pygame.K_s:
                    writetosave(path,objects)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
             radius += 1
             print(radius)
        if keys[pygame.K_DOWN]:
             if radius > 10:
               radius -= 1

        win.fill('black')
        for thing in objects:
             thing.draw(win)
        if selectedshape == 1:
          pygame.draw.circle(win,(255,200,200),(mouse_x,mouse_y),radius)
        elif selectedshape ==2:
          pygame.draw.rect(win,(255,100,100),(mouse_x-math.sqrt(radius**2/2),mouse_y-math.sqrt(radius**2/2),2*math.sqrt(radius**2/2),2*math.sqrt(radius**2/2)))

        elif selectedshape ==4:
            pygame.draw.circle(win,(100,255,100),(mouse_x,mouse_y),radius)
            pygame.draw.circle(win,(200,200,200),(mouse_x,mouse_y),(radius+1)//1.2)
        elif selectedshape ==3:
            pygame.draw.circle(win,(100,100,100),(mouse_x,mouse_y),radius)
            pygame.draw.circle(win,(200,200,200),(mouse_x,mouse_y),(radius+1)//1.2)

        pygame.display.update()

