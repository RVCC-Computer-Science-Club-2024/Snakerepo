import pygame, sys
from pygame.locals import QUIT

pygame.init() # Initializes pygame module
display_surface = pygame.display.set_mode((400, 300)) # Sets window size
pygame.display.set_caption('Snake') # Sets window title
clock = pygame.time.Clock()

while True:
   for event in pygame.event.get(): #Gets a list of all events
       if event.type == QUIT: # Checks if X is clicked
           pygame.quit() # Closes window
           sys.exit() # Closes program
    
    
   pygame.display.update() # Updates screen; completes 1 game loop
   