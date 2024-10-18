from rich.traceback import install; install()
from rich import print
import pygame, sys
from pygame.locals import QUIT

class Snake:
    def __init__(self) -> None:
        """
        Constructor to initialize the snake.
        Initializes a body with 1 head tile at 0,0.
        """
        self.body = [[0,0,pygame.Surface((10, 10))]]
        self.body[0][2].fill("white")
    
    def move(self, direction, eaten = False):
        """
        Moves the snake in a specified direction.

        Args:
            direction: Specify the direction in which to move the snake.
            eaten (bool, optional): Specify whether the snake has eaten this iteration. Defaults to False.
        """
        head = self.body[0]
        newhead = [0,0,None]
        # TODO:
        # ENTER SCREEN-WRAP CHECK BELOW
        if direction == "left":
            newhead = [head[0]-10, head[1]]
        elif direction == "right":
            newhead = [head[0]+10, head[1]]
        elif direction == "up":
            newhead = [head[0], head[1]-10]
        elif direction == "down":
            newhead = [head[0], head[1]+10]
            
        # TODO:
        # ENTER DEATH CHECK HERE
        
        
        try:    # Throws an error if direction = None
            newhead.append(pygame.Surface((10, 10)))
            newhead[2].fill("white")
            self.body.insert(0, newhead)
            
            if not eaten:
                self.body.pop()
        except: # Expected exception, no need to handle
            pass







def main():
    """
    Main loop: Run upon execution.
    Initializes board, variables and begins pygame window-loop.
    """
    snake = Snake() # Create snake
    
    pygame.init() # Initializes pygame module
    clock = pygame.time.Clock() # FPS object
    background = pygame.display.set_mode((500, 400)) # Sets window size
    pygame.display.set_caption("Snake") # Sets window title
    direction = None
    loop_ctr = 1
    apple = False
    
    while True:
        """
        Pygame window-loop. Exits upon closing the window
        """
        
        # Event checking
        for event in pygame.event.get(): # Gets a list of all events
            if event.type == QUIT: # Checks if X is clicked
                pygame.quit() # Closes window
                sys.exit() # Closes program
            
            if event.type == pygame.KEYDOWN: # Checks if left,right,up or down arrow keys were pressed
                if event.key == pygame.K_LEFT:
                    direction = "left"
                if event.key == pygame.K_RIGHT:
                    direction = "right"
                if event.key == pygame.K_UP:
                    direction = "up"
                if event.key == pygame.K_DOWN:
                    direction = "down"
                if event.key == pygame.K_SPACE:
                    apple = True if not apple else False
                
        # TODO:
        # On set time intervals, randomly decide whether or not to generate an apple if not present already.
        # Add apple-bag power-up
        # Sprites
        # Convert to exe

        # Move snake head when loop_ctr has reset
        # !!!!! Bad solution as loops are unreliable measurements of time. Consider instead replacing with a time module timer, or using clock.time()/clock.raw_time()
        if loop_ctr == 1:
            snake.move(direction,apple)
        
        # Refill background
        background.fill((0, 100, 50)) # Sets background color
        
        # Draw objects (in this case: snake)
        for tile in snake.body:
            background.blit(tile[2],(tile[0], tile[1]))
            
        # Game loop
        pygame.display.flip() # Updates screen
        clock.tick(60) # Ensures a max of 60 FPS
        if loop_ctr % (50) == 0: # Loop counter - resets every 50 loops, 
            loop_ctr = 1
        else:
            loop_ctr += 1
        pygame.display.update() # Updates screen; completes 1 game loop

if __name__ == "__main__":
    main() # Godspeed :saluting_face:
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
