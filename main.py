from rich.traceback import install; install()
from rich import print
import pygame, sys, os, random
from time import sleep
from math import floor
from pygame.locals import QUIT

# TODO:
# Win code
# Background grid pattern
# Better score counter
# Audio
# Code cleanup
# Apple bags
# Fix timer (maybe good enough solution?)

# BUG:
# Upon death & during extra frame, snake looks goofy asf -> maybe need more head sprites? Maybe look into rotating/flipping images?
# Insta-restart bug
# Extra frame can last forever
# Does not go translucent on death




# Game is updated/cycled every LOOP_DELAY loops
# In other words, ~Loop execution time/LOOP_DELAY seconds per loop
#       >>>>      WTF IS LOOP EXECUTION TIME???  There has to be a better way to measure loop time than this    <<<<<
#       >>>>      Refer to "Move snake head when loop_ctr has reset" comment in main loop ~line 240             <<<<<

LOOP_DELAY = 10             # We don't want the game running this fast, or the snake ZOOMS, so we delay the game loop by this many loops

FPS = 60                    # Ensures that at LEAST this many frames render per loop
HEIGHT = 500
WIDTH = 500
GRID_SIZE = (20,20)
TILE_DIMENSIONS = (WIDTH/GRID_SIZE[0], HEIGHT/GRID_SIZE[1])     # Calculate dimensions of snake tile based on grid & and window dimensions
PAUSE_DELAY = 3000          # Number of milliseconds to wait before unpausing
EXTRA_FRAMES = 500          # Number of extra milliseconds to give upon imminent death
DARK_GREEN = "#006432"      # Background color
START_LENGTH = 3

paused = [True, "START"]
background = pygame.display.set_mode((WIDTH, HEIGHT))           # Sets window size
input_disable_guardrail = False



def get_path(file_path):
    return os.path.join(os.path.dirname(__file__), file_path)


class Snake:
    """
    Snake class that contains the snake body to be displayed in the game, 
    along with associated methods to manipulate it.
    """
    def __init__(self) -> None:
        """
        Constructor to initialize the snake.
        Initializes a body with 1 head tile at a random location.
        """
        self.body = [[random.randint(0,GRID_SIZE[0]-1)*TILE_DIMENSIONS[0],random.randint(0,GRID_SIZE[1]-1)*TILE_DIMENSIONS[1],pygame.image.load(get_path("assets/head_up.png")).convert_alpha()]]
        
        # Add more body tiles to begin with
        for _ in range(START_LENGTH-1):
            self.move(pygame.K_UP, spawn_apple(self, self.body[0][0], self.body[0][1]))
    
    def move(self, direction, apple: list) -> bool:
        """
        Moves the snake in a specified direction.

        Args:
            direction (pygame Key Code): Specify the direction in which to move the snake.
            apple (list): Apple object.
        
        Returns:
            bool: Returns whether the snake has eaten this iteration.
        """
        global paused, background, input_disable_guardrail
        
        if paused[0] and paused[1] == "EXTRA FRAME":
            paused = [False,""]
            return False
        
        head = self.body[0]
        newhead = [0,0,None]
        
        if direction == pygame.K_LEFT:
            if head[0] == 0:                                    # Screen wrap check
                newhead = [WIDTH-TILE_DIMENSIONS[0], head[1]]
            else:
                newhead = [head[0]-TILE_DIMENSIONS[0], head[1]]
        elif direction == pygame.K_RIGHT:
            if head[0] == WIDTH-TILE_DIMENSIONS[0]:             # Screen wrap check
                newhead = [0, head[1]]
            else:
                newhead = [head[0]+TILE_DIMENSIONS[0], head[1]]
        elif direction == pygame.K_UP:
            if head[1] == 0:                                    # Screen wrap check
                newhead = [head[0], HEIGHT-TILE_DIMENSIONS[1]]
            else:
                newhead = [head[0], head[1]-TILE_DIMENSIONS[1]]
        elif direction == pygame.K_DOWN:
            if head[1] == HEIGHT-TILE_DIMENSIONS[1]:            # Screen wrap check
                newhead = [head[0], 0]
            else:
                newhead = [head[0], head[1]+TILE_DIMENSIONS[1]]
        
        
        # Checks if snake has eaten apple, if so, grow snake
        eaten = False
        if newhead[0] == apple[0] and newhead[1] == apple[1]:
            eaten = True
            # print(f"Snake length increased to: {len(self.body)}")
        
        
        # Add extra frame if snake is about to collide with itself
        if paused[1] != "EXTRA FRAME LIFTED":   # Prevent infinite extra frames
            for tile in self.body[2:]:
                if newhead[0] == tile[0] and newhead[1] == tile[1]:
                    paused = [True, "EXTRA FRAME"]
        else:
            paused[1] = ""
        
        
        # Checks if snake has hit itself, if so, color it grey and end game
        if not paused[0]:
            for tile in self.body[1:]:
                if newhead[0] == tile[0] and newhead[1] == tile[1]:
                    paused = [True, "DEATH"]
                    
                    # Blink snake body for 5 cycles upon death
                    for _ in range(5):
                        for _,_,tile in self.body:
                            tile.set_alpha(0)
                            update_screen(snake=self, apple=apple)
                        sleep(0.25)
                        for _,_,tile in self.body:
                            tile.set_alpha(255)
                            update_screen(snake=self, apple=apple)
                        sleep(0.25)
        
        
        if not paused[0] or paused[1] == "START":
            newhead.append(pygame.Surface(TILE_DIMENSIONS))
            # By default, snake body has purple-black checkered missing texture
            if len(self.body)%2 == 0:
                newhead[2].fill("purple")
            else:
                newhead[2].fill("black")
            if paused[1] != "EXTRA FRAME":
                self.body.insert(0, newhead)
            
            if not eaten and not paused[0]:     # Pops tail if snake has not eaten and game is not paused
                self.body.pop()
        
        # Re-enable movement
        input_disable_guardrail = False
        
        # Apply assets to snake body
        self.apply_assets(direction)
        
        return eaten    # Returns whether snake has eaten this frame or not
    
    def apply_assets(self, direction) -> None:
        """_summary_

        Args:
            direction (_type_): _description_
        """ # Add asset for head
        if direction == pygame.K_LEFT:
            self.body[0][2] = pygame.image.load(get_path("assets/head_left.png")).convert_alpha()
        elif direction == pygame.K_RIGHT:
            self.body[0][2] = pygame.image.load(get_path("assets/head_right.png")).convert_alpha()
        elif direction == pygame.K_UP:
            self.body[0][2] = pygame.image.load(get_path("assets/head_up.png")).convert_alpha()
        elif direction == pygame.K_DOWN:
            self.body[0][2] = pygame.image.load(get_path("assets/head_down.png")).convert_alpha()
        self.body[0][2] = pygame.transform.scale(self.body[0][2], TILE_DIMENSIONS)
        
        
        piece_1, piece_2 = self.body[0], self.body[1]
        # Add assets for body
        for piece_3 in self.body[2:]:
            # For piece_1 - piece_2 - piece_3, alter the texture on locations of piece_1 and piece_2
            if piece_2[0] == piece_1[0] and piece_2[0] == piece_3[0]:   # Horizontal body
                piece_2[2] = pygame.image.load(get_path("assets/body_vertical.png"))
            elif piece_2[1] == piece_1[1] and piece_2[1] == piece_3[1]:   # Vertical body
                piece_2[2] = pygame.image.load(get_path("assets/body_horizontal.png"))
            
            elif piece_1[0] < piece_2[0]:         # Piece_1 is to the left of piece_2
                if piece_2[1] < piece_3[1]:     # Piece_2 is above piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
                elif piece_2[1] > piece_3[1]:    # Piece_2 is below piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
            elif piece_1[0] > piece_2[0]:        # Piece_1 is to the right of piece_2
                if piece_2[1] < piece_3[1]:      # Piece_2 is above piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                elif piece_2[1] > piece_3[1]:    # Piece_2 is below piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
            elif piece_1[1] < piece_2[1]:        # Piece_1 is above piece_2
                if piece_2[0] < piece_3[0]:      # Piece_2 is to the left of piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
                elif piece_2[0] > piece_3[0]:    # Piece_2 is to the right of piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
            elif piece_1[1] > piece_2[1]:        # Piece_1 is below piece_2
                if piece_2[0] < piece_3[0]:      # Piece_2 is to the left of piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                elif piece_2[0] > piece_3[0]:    # Piece_2 is to the right of piece_3
                    piece_2[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
            piece_2[2] = pygame.transform.scale(piece_2[2], TILE_DIMENSIONS)
            piece_1, piece_2 = piece_2, piece_3
        
        # Add assets for tail
        if self.body[-1][0] < self.body[-2][0]:     # Tail is to the left of the body
            self.body[-1][2] = pygame.image.load(get_path("assets/tail_left.png")).convert_alpha()
        elif self.body[-1][0] > self.body[-2][0]:   # Tail is to the right of the body
            self.body[-1][2] = pygame.image.load(get_path("assets/tail_right.png")).convert_alpha()
        elif self.body[-1][1] < self.body[-2][1]:   # Tail is above the body
            self.body[-1][2] = pygame.image.load(get_path("assets/tail_up.png")).convert_alpha()
        elif self.body[-1][1] > self.body[-2][1]:   # Tail is below the body
            self.body[-1][2] = pygame.image.load(get_path("assets/tail_down.png")).convert_alpha()
        self.body[-1][2] = pygame.transform.scale(self.body[-1][2], TILE_DIMENSIONS)


def update_screen(*args: tuple, snake: Snake, apple: list) -> None:
    """Draws objects to the screen and updates it

    Args:
        *args (tuple): Additional objects to be drawn to screen.\n
                       Objects must be in the form of (Surface, x, y)
        snake (Snake): Snake object.
        apple (list): Apple object.
    """
    global background
    # Refill background
    background.fill(DARK_GREEN) # Sets background color

    # Draw grid
    for row in TILE_DIMENSIONS[1]:
        for tile in TILE_DIMENSIONS[0]:
            pass # WIP
    
    # Draw snake
    for tile in snake.body:
        background.blit(tile[2],(tile[0], tile[1]))
    
    # Draw apple
    background.blit(apple[2],(apple[0], apple[1]))
    
    # Update score counter
    score_font = pygame.font.Font(None, 36) # Font object for score
    score_counter = score_font.render(str(len(snake.body)-START_LENGTH), 1, (255, 255, 255))
    background.blit(score_counter, (WIDTH/2, TILE_DIMENSIONS[1]/2))
    
    # Draw other objects
    for arg in args:
        background.blit(arg[0],(arg[1], arg[2]))
    
    # Update screen
    pygame.display.update()

def keyboard_inputs():
    pass
    # For future code cleanup purposes

def spawn_apple(snake: Snake, x: float = 0, y: float = 0) -> list:
    """
    Spawns an apple on a random position on the board.

    Args:
        snake (Snake): Snake object.
        x (float, optional): X position of the apple. Defaults to 0.
        y (float, optional): Y position of the apple. Defaults to 0.
        
    Returns:
        list: Apple object with co-ordinates and surface.
    """
    # Checks if apple can be spawned on the board
    good_coordinates_flag = False
    while not good_coordinates_flag:
        x,y = random.randint(0, GRID_SIZE[0]-1)*TILE_DIMENSIONS[0], random.randint(0, GRID_SIZE[1]-1)*TILE_DIMENSIONS[1]
        snake_coords = [tile[:2] for tile in snake.body]
        good_coordinates_flag = not [x,y] in snake_coords
    apple = [x, y, pygame.image.load(get_path("assets/apple.png")).convert_alpha()]
    apple[2] = pygame.transform.scale(apple[2], TILE_DIMENSIONS)
    # print(f"Apple spawned at: {apple[0]/TILE_DIMENSIONS[0]},{apple[1]/TILE_DIMENSIONS[1]}", end="\r")
    
    return apple



def main():
    """
    Main loop: Run upon execution.
    Initializes board, variables and begins pygame window-loop.
    """
    global paused, background, input_disable_guardrail
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
                    if event.key in dont_move_this_way.keys() and dont_move_this_way[event.key] != direction and not input_disable_guardrail:
                        direction = event.key
                        # Disable movement until 1 movement has been done
                        input_disable_guardrail = True
                    
                    # Pause when ESC is pressed
                    if event.key == pygame.K_ESCAPE:
                        paused = [True, "PAUSE"]
                        
            else:
                if paused[1] in ("PAUSE", "START"):
                # Gray out tiles when paused
                    for _,_,tile in snake.body:
                        tile.set_alpha(128)
                        
                    if event.type == pygame.KEYDOWN:
                        # Delay for 3 seconds before unpausing
                        for i in range(PAUSE_DELAY):
                            if i%10**3 == 0:
                                # Display time remaining until unpausing
                                pause_font = pygame.font.Font(None, 36) # Font object for pause message
                                text_pause = pause_font.render(str(round(floor(PAUSE_DELAY/10**3) - i/10**3)), 1, (255, 255, 255))
                                update_screen((text_pause, WIDTH/2, HEIGHT/2),snake=snake, apple=apple)
                                pygame.display.update()
                            sleep(10**-3)
                        
                        # White back tiles when unpaused
                        for _,_,tile in snake.body:
                            tile.set_alpha(255)
                            
                        # Update move direction when unpausing <----- LIFEHACK 👀
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                            direction = event.key
                            
                        # Unpause
                        paused = [False,""]
                
                elif paused[1] == "EXTRA FRAME":
                    # Wait for given amount of time
                    sleep(EXTRA_FRAMES*10**-3)
                    # Unpause
                    paused = [False,"EXTRA FRAME LIFTED"]
                
                elif paused[1] == "DEATH":
                    for _,_,tile in snake.body:
                        tile.set_alpha(128) # Makes snake body translucent upon death
                        tile.set_colorkey((20,0,0))
                        update_screen(snake=snake, apple=apple)
                    if event.type == pygame.KEYDOWN:
                        input_disable_guardrail = False
                        paused = [True, "START"]
                        snake = Snake()
                        apple = spawn_apple(snake)
                        loop_ctr = 1
                    
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

        update_screen(snake=snake, apple=apple)
        
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