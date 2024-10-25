from rich.traceback import install; install()
from rich import print
import pygame, sys, random
from time import sleep
from pygame.locals import QUIT
from PIL import Image,ImageFilter

# TODO:
# Win code
# Lose code
# Icons/Sprites
# Audio
# Leaderboards
# Fix timer (maybe good enough solution?)
# Apples
# Apple bags
# Add pause
# Convert to exe
# Check viability on mav



FPS = 60
HEIGHT = 500
WIDTH = 500
GRID_SIZE = (20,20)
# Calculate dimensions of snake tile based on grid & and window dimensions
TILE_DIMENSIONS = (WIDTH/GRID_SIZE[0], HEIGHT/GRID_SIZE[1])
PAUSE_DELAY = 0

paused = (True, "START")
background = pygame.display.set_mode((WIDTH, HEIGHT)) # Sets window size




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
        self.body = [[random.randint(0,GRID_SIZE[0]-1)*TILE_DIMENSIONS[0],random.randint(0,GRID_SIZE[1]-1)*TILE_DIMENSIONS[1],pygame.Surface(TILE_DIMENSIONS)]]
        self.body[0][2].fill("white")
    
    def move(self, direction, apple):
        """
        Moves the snake in a specified direction.

        Args:
            direction: Specify the direction in which to move the snake.
            eaten (bool, optional): Specify whether the snake has eaten this iteration. Defaults to False.
        """
        global paused,background
        
        head = self.body[0]
        newhead = [0,0,None]
        
        if direction == pygame.K_LEFT:
            if head[0] == 0:                                    # Screen wrap check
                newhead = [WIDTH-TILE_DIMENSIONS[0], head[1]]
            else:
                newhead = [head[0]-TILE_DIMENSIONS[0], head[1]]
        elif direction == pygame.K_RIGHT:
            if head[0] == WIDTH-TILE_DIMENSIONS[0]:            # Screen wrap check
                newhead = [0, head[1]]
            else:
                newhead = [head[0]+TILE_DIMENSIONS[0], head[1]]
        elif direction == pygame.K_UP:
            if head[1] == 0:                                    # Screen wrap check
                newhead = [head[0], HEIGHT-TILE_DIMENSIONS[1]]
            else:
                newhead = [head[0], head[1]-TILE_DIMENSIONS[1]]
        elif direction == pygame.K_DOWN:
            if head[1] == HEIGHT-TILE_DIMENSIONS[1]:           # Screen wrap check
                newhead = [head[0], 0]
            else:
                newhead = [head[0], head[1]+TILE_DIMENSIONS[1]]
           
        # Checks if snake has eaten apple, if so, grow snake
        eaten = False
        if apple:
            if newhead[0] == apple[0] and newhead[1] == apple[1]:
                eaten = True
                print(f"Snake length increased to: {len(self.body)}")
        
        
        # Checks if snake has hit itself, if so, color it red and end game
        for tile in self.body[1:]:
            if newhead[0] == tile[0] and newhead[1] == tile[1]:
                paused = (True, "DEATH")
                # Color snake red
                for _ in range(5):
                    for x,y,tile in self.body:
                        tile.fill("#006432")
                        background.blit(tile,(x, y))
                    pygame.display.flip() 
                    sleep(0.25)
                    for x,y,tile in self.body:
                        tile.fill("#888888")
                        background.blit(tile,(x, y))
                    pygame.display.flip() 
                    sleep(0.25)
                
                
                for _,_,tile in self.body[1:]:
                    tile.fill("#888888")
        
        
        
        try:    # Throws an error if direction = None
            newhead.append(pygame.Surface(TILE_DIMENSIONS))           
            newhead[2].fill("white")
            self.body.insert(0, newhead)
            
            if not eaten and not paused[0]:     # Pops tail if snake has not eaten and game is not paused
                self.body.pop()
        except: # Expected exception, no need to handle
            pass
        
        return eaten    # Returns whether snake has eaten this frame or not




def main():
    """
    Main loop: Run upon execution.
    Initializes board, variables and begins pygame window-loop.
    """
    global paused, background
    snake = Snake() # Create snake
    
    pygame.init() # Initializes pygame module
    pygame.display.set_caption("Snake") # Sets window title
    clock = pygame.time.Clock() # FPS object
    direction = pygame.K_RIGHT
    loop_ctr = 1
    apple = None
    
    while True:
        """
        Pygame window-loop. Exits upon closing the window
        """
        
        # Event checking
        for event in pygame.event.get():    # Gets a list of all events
            if event.type == QUIT:          # Checks if X is clicked
                pygame.quit()               # Closes window
                sys.exit()                  # Closes program
            
            if not paused[0]:   # Pause check
                if event.type == pygame.KEYDOWN:
                    # Update move direction
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                        direction = event.key
                        
            else:
                if paused[1] == "PAUSE":
                # Gray out tiles when paused
                    for _,_,tile in snake.body[1:]:
                        tile.fill("#777777")
                elif paused[1] == "START":
                    snake.body[0][2].fill("#777777")
                elif paused[1] == "DEATH":
                    pass
                    # TODO:
                    # What do we do on death?
                elif paused[1] == "WIN":
                    pass
                    # TODO:
                    # What do we do on win?
                    
                
                if paused[1] in ("PAUSE", "START"):
                    if event.type == pygame.KEYDOWN:
                        # Delay for 3 seconds before unpausing
                        for i in range(PAUSE_DELAY):
                            print(f"Unpausing in {PAUSE_DELAY - i}...", end="\r")
                            sleep(1)
                            
                        # Update move direction when unpausing <----- LIFEHACK 👀
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                            direction = event.key
                            
                        # Unpause
                        paused = (not paused[0], paused[1])
        
                
        # TODO:
        # On set time intervals, randomly decide whether or not to generate an apple if not present already.
        # Add apple-bag power-up

        # Randomly generate apple on board
        if not apple and not paused[0]:
            good_coordinates_flag = False
            while not good_coordinates_flag:
                x,y = random.randint(0, GRID_SIZE[0]-1)*TILE_DIMENSIONS[0], random.randint(0, GRID_SIZE[1]-1)*TILE_DIMENSIONS[1]
                snake_coords = [tile[:2] for tile in snake.body]
                good_coordinates_flag = not [x,y] in snake_coords
            apple = (x, y, pygame.Surface(TILE_DIMENSIONS))
            apple[2].fill("red")
            print(f"Apple spawned at: {apple[0]/TILE_DIMENSIONS[0]},{apple[1]/TILE_DIMENSIONS[1]}", end="\r")
        
        
        # Move snake head when loop_ctr has reset
        # !!!!! Bad solution as loops are unreliable measurements of time. Consider instead replacing with a time module timer, or using clock.time()/clock.raw_time()
        if loop_ctr == 1 and not paused[0]:
            eaten = snake.move(direction, apple)
            apple = None if eaten else apple
        
        # Refill background
        background.fill("#006432") # Sets background color
        
        # Draw objects (in this case: snake)
        for tile in snake.body:
            background.blit(tile[2],(tile[0], tile[1]))
        if apple:
            background.blit(apple[2],(apple[0], apple[1]))
            
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