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
# Apple bags
# Add pause
# Convert to exe
# Check viability on mav



# Game is updated/cycled every LOOP_DELAY loops
# In other words, ~Loop execution time/LOOP_DELAY seconds per loop
#       >>>>      WTF IS LOOP EXECUTION TIME???  There has to be a better way to measure loop time than this    <<<<<
#       >>>>      Refer to "Move snake head when loop_ctr has reset" comment in main loop ~line 240             <<<<<

LOOP_DELAY = 10         # We don't want the game running this fast, or the snake ZOOMS, so we delay the game loop by this many loops

FPS = 60                # Ensures that at LEAST this many frames render per loop
HEIGHT = 500
WIDTH = 500
GRID_SIZE = (20,20)
TILE_DIMENSIONS = (WIDTH/GRID_SIZE[0], HEIGHT/GRID_SIZE[1])     # Calculate dimensions of snake tile based on grid & and window dimensions
PAUSE_DELAY = 3

DARK_GREEN = "#006432"

paused = (True, "START")
background = pygame.display.set_mode((WIDTH, HEIGHT))           # Sets window size
movement_disabled = False




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
        # Add 2 more body tiles
        for i in range(2):
            makeshift_food = (self.body[0][0], self.body[0][1])
            self.move(pygame.K_UP, makeshift_food)
    
    def move(self, direction, apple):
        """
        Moves the snake in a specified direction.

        Args:
            direction: Specify the direction in which to move the snake.
            eaten (bool, optional): Specify whether the snake has eaten this iteration. Defaults to False.
        """
        global paused, background, movement_disabled
        
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
        if newhead[0] == apple[0] and newhead[1] == apple[1]:
            eaten = True
            print(f"Snake length increased to: {len(self.body)}")
        
        
        # Checks if snake has hit itself, if so, color it red and end game
        for tile in self.body[1:]:
            if newhead[0] == tile[0] and newhead[1] == tile[1]:
                paused = (True, "DEATH")
                
                # Blink snake body
                for _ in range(5):
                    for x,y,tile in self.body:
                        tile.fill(DARK_GREEN)
                        background.blit(tile,(x, y))
                    pygame.display.flip() 
                    sleep(0.25)
                    for x,y,tile in self.body:
                        tile.fill("#888888")
                        background.blit(tile,(x, y))
                    pygame.display.flip() 
                    sleep(0.25)
        
        
        try:    # Throws an error if direction = None
            newhead.append(pygame.Surface(TILE_DIMENSIONS))           
            newhead[2].fill("white")
            self.body.insert(0, newhead)
            
            if not eaten and not paused[0]:     # Pops tail if snake has not eaten and game is not paused
                self.body.pop()
        except: # Expected exception, no need to handle
            pass
        
        # Re-enable movement
        movement_disabled = False
        
        return eaten    # Returns whether snake has eaten this frame or not



def spawn_apple(snake) -> tuple:
    """
    Spawns an apple on a random position on the board.

    Args:
        snake (Snake): Snake object.
        
    Returns:
        tuple: Apple object with co-ordinates and surface.
    """
    good_coordinates_flag = False
    while not good_coordinates_flag:
        x,y = random.randint(0, GRID_SIZE[0]-1)*TILE_DIMENSIONS[0], random.randint(0, GRID_SIZE[1]-1)*TILE_DIMENSIONS[1]
        snake_coords = [tile[:2] for tile in snake.body]
        good_coordinates_flag = not [x,y] in snake_coords
    apple = (x, y, pygame.Surface(TILE_DIMENSIONS))
    apple[2].fill("red")
    print(f"Apple spawned at: {apple[0]/TILE_DIMENSIONS[0]},{apple[1]/TILE_DIMENSIONS[1]}", end="\r")
    
    return apple



def main():
    """
    Main loop: Run upon execution.
    Initializes board, variables and begins pygame window-loop.
    """
    global paused, background, movement_disabled
    snake = Snake() # Create snake
    
    pygame.init() # Initializes pygame module
    pygame.display.set_caption("Snake") # Sets window title
    clock = pygame.time.Clock() # FPS object
    direction = pygame.K_RIGHT
    loop_ctr = 1
    # Create apple and ensure it does not spawn on the initial snake head
    apple = spawn_apple(snake)
    
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
                    # Guard-rails so you can't die by moving directly backwards into yourself
                    dont_move_this_way = {pygame.K_LEFT: pygame.K_RIGHT, pygame.K_RIGHT: pygame.K_LEFT, pygame.K_UP: pygame.K_DOWN, pygame.K_DOWN: pygame.K_UP}
                    # Update move direction
                    if event.key in dont_move_this_way.keys() and dont_move_this_way[event.key] != direction and not movement_disabled:
                        direction = event.key
                        # Disable movement until 1 movement has been done
                        movement_disabled = True
                    
                    # Pause when ESC is pressed
                    if event.key == pygame.K_ESCAPE:
                        paused = (True, "PAUSE")
                        
            else:
                if paused[1] in ("PAUSE", "START"):
                # Gray out tiles when paused
                    for _,_,tile in snake.body[1:]:
                        tile.fill("#777777")
                        
                    if event.type == pygame.KEYDOWN:
                        # Delay for 3 seconds before unpausing
                        for i in range(PAUSE_DELAY):
                            # print(f"Unpausing in {PAUSE_DELAY - i}...", end="\r")

                            font = pygame.font.Font(None, 36)
                            textPause = font.render(str(PAUSE_DELAY - i), 1, (255, 255, 255))
                            background.blit(textPause, (WIDTH // 2, HEIGHT // 2))
                            pygame.display.update()
                            background.fill(DARK_GREEN)
                            for tile in snake.body[1:]:
                                background.blit(tile[2], (tile[0], tile[1]))
                            background.blit(apple[2], (apple[0], apple[1]))
                            sleep(1)
                        
                        # White back tiles when unpaused
                        for _,_,tile in snake.body[1:]:
                            tile.fill("white")
                            
                        # Update move direction when unpausing <----- LIFEHACK 👀
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                            direction = event.key
                            
                        # Unpause
                        paused = (not paused[0], paused[1])
                        
                elif paused[1] == "DEATH":
                    pass
                    # TODO:
                    # What do we do on death?
                    
                elif paused[1] == "WIN":
                    pass
                    # TODO:
                    # What do we do on win?
                        
        
        # Move snake head when loop_ctr has reset
        # !!!!! Bad solution as loops are unreliable measurements of time. Consider instead replacing with a time module timer, or using clock.time()/clock.raw_time()
        if loop_ctr == 1 and not paused[0]:
            eaten = snake.move(direction, apple)
            apple = spawn_apple(snake) if eaten else apple

        
        # TODO:
        # Add apple-bag power-up
        
        
        # Refill background
        background.fill(DARK_GREEN) # Sets background color
        
        # Draw objects
        for tile in snake.body:
            background.blit(tile[2],(tile[0], tile[1]))
        background.blit(apple[2],(apple[0], apple[1]))
            
        # Game loop
        pygame.display.flip() # Updates screen, completes one loop
        clock.tick(FPS) # Ensures a max of 60 FPS
        if loop_ctr % (LOOP_DELAY) == 0: # Loop counter - resets every 50 loops, 
            loop_ctr = 1
        else:
            loop_ctr += 1
        pygame.display.update() # Updates screen; completes 1 game loop



if __name__ == "__main__":
    main() # Godspeed 🫡