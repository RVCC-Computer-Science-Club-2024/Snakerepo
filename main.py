from rich.traceback import install; install()
from rich import print
import pygame, sys
from pygame.locals import QUIT


FPS = 60
HEIGHT = 400
WIDTH = 500
GRID_SIZE = (20,20)
# Calculate dimensions of snake tile based on grid & and window dimensions
SNAKE_DIMENSIONS = (WIDTH/GRID_SIZE[0], HEIGHT/GRID_SIZE[1])

paused = (False, "")


class Snake:
    """
    Snake class that contains the snake body to be displayed in the game, 
    along with associated methods to manipulate it.
    """
    def __init__(self) -> None:
        """
        Constructor to initialize the snake.
        Initializes a body with 1 head tile at 0,0.
        """
        self.body = [[0,0,pygame.Surface(SNAKE_DIMENSIONS)]]
        self.body[0][2].fill("white")
    
    def move(self, direction, eaten = False):
        """
        Moves the snake in a specified direction.

        Args:
            direction: Specify the direction in which to move the snake.
            eaten (bool, optional): Specify whether the snake has eaten this iteration. Defaults to False.
        """
        global paused
        
        head = self.body[0]
        newhead = [0,0,None]
        
        if direction == "left":
            if head[0] == 0:                                    # Screen wrap check
                newhead = [WIDTH-SNAKE_DIMENSIONS[0], head[1]]
            else:
                newhead = [head[0]-SNAKE_DIMENSIONS[0], head[1]]
        elif direction == "right":
            if head[0] == WIDTH-SNAKE_DIMENSIONS[0]:            # Screen wrap check
                newhead = [0, head[1]]
            else:
                newhead = [head[0]+SNAKE_DIMENSIONS[0], head[1]]
        elif direction == "up":
            if head[1] == 0:                                    # Screen wrap check
                newhead = [head[0], HEIGHT-SNAKE_DIMENSIONS[1]]
            else:
                newhead = [head[0], head[1]-SNAKE_DIMENSIONS[1]]
        elif direction == "down":
            if head[1] == HEIGHT-SNAKE_DIMENSIONS[1]:           # Screen wrap check
                newhead = [head[0], 0]
            else:
                newhead = [head[0], head[1]+SNAKE_DIMENSIONS[1]]
           
        
        # Checks if snake has hit itself, if so, highlight head as red and end game
        for tile in self.body[1:]:
            if newhead[0] == tile[0] and newhead[1] == tile[1]:
                print("DEATH")
                paused = (True, "DEATH")
                self.body[0][2].fill("red")
        
        
        
        try:    # Throws an error if direction = None
            newhead.append(pygame.Surface(SNAKE_DIMENSIONS))           
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
    global paused
    snake = Snake() # Create snake
    
    pygame.init() # Initializes pygame module
    clock = pygame.time.Clock() # FPS object
    background = pygame.display.set_mode((WIDTH, HEIGHT)) # Sets window size
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
        # Convert to exe, add installation commands, check if works on mac

        # Move snake head when loop_ctr has reset
        # !!!!! Bad solution as loops are unreliable measurements of time. Consider instead replacing with a time module timer, or using clock.time()/clock.raw_time()
        if loop_ctr == 1 and paused[0] == False:
            snake.move(direction,apple)
        
        # Refill background
        background.fill((0, 100, 50)) # Sets background color
        
        # Draw objects (in this case: snake)
        for tile in snake.body:
            background.blit(tile[2],(tile[0], tile[1]))
            
        # Game loop
        pygame.display.flip() # Updates screen, completes one loop
        clock.tick(FPS) # Ensures a max of 60 FPS
        if loop_ctr % (10) == 0: # Loop counter - resets every 50 loops, 
            loop_ctr = 1
        else:
            loop_ctr += 1
        pygame.display.update() # Updates screen; completes 1 game loop



if __name__ == "__main__":
    main() # Godspeed 🫡