from rich.traceback import install; install()
from rich import print
import pygame, sys, os, random
from math import floor
from pygame.locals import QUIT

# TODO
# ===========================================================================
# >>>> PRIORITY: HIGH <<<<
# Win code
# Better score counter
# Audio
# Make background grid pattern less jank

# >>>> PRIORITY: MEDIUM <<<<
# Code cleanup
# Apple bags
# Fix timer (maybe good enough solution?)

# BUG
# ===========================================================================
# >>>> PRIORITY: LOW <<<<
# Upon death & during extra frame, snake looks goofy asf -> maybe need more head sprites? Maybe look into rotating/flipping images?
# If start length is 8 or higher, chance that the snake spawns soft-locked


# CONSTANTS
# ===========================================================================

FPS = 60                    # Maximum FPS, to avoid CPU overload
LOOP_DELAY = 10             # We want the game rendered with FPS, 
                            # but don't want the code logic to be executed every frame.
                            # The game logic is executed every LOOP_DELAY iterations of the main() loop
                            
HEIGHT = 500                # Window height
WIDTH = 500                 # Window width
GRID_SIZE = (10,10)         # Number of tiles in the grid
TILE_DIMENSIONS = (WIDTH//GRID_SIZE[0], HEIGHT//GRID_SIZE[1])   # Calculate dimensions of snake tile based on grid & and window dimensions
PAUSE_DELAY = 3000          # Number of milliseconds to wait before unpausing
EXTRA_FRAMES = 500          # Number of extra milliseconds to give upon imminent death
INITIAL_SNAKE_LENGTH = 3    # Number of tiles the snake starts with --- Minimum is 3
DIRECTION_BUFFER_LENGTH = 3 # Max number of keystrokes to queue up at once
WIN_SCORE_THRESHOLD = 10    # Score threshold to win

DARK_GREEN = "#006432"      # Background color

# GLOBAL VARRIABLES
# ===========================================================================
paused = [True, "START"]                                        # List that stores pause state and reason
background = pygame.display.set_mode((WIDTH, HEIGHT))           # Creates a pygame window object with given dimensions



def get_path(file_path: str) -> str:
    """
    Returns the absolute path of a desired file

    Args:
        file_path (str): Relative path to the desired file

    Returns:
        str: Absolute path to the desired file
    """
    return os.path.join(os.path.dirname(__file__), file_path)


class Snake:
    """
    Snake class that contains the snake body to be displayed in the game, \n
    along with associated methods to manipulate it.
    """
    def __init__(self) -> None:
        """
        Constructor to initialize the snake. \n
        Initializes a body with a random shape at a random location on the grid. \n
        Spawns initial apple via spawn_apple() method
        """
        # Initialize body
        self.body = [[random.randint(0,GRID_SIZE[0]-1)*TILE_DIMENSIONS[0],random.randint(0,GRID_SIZE[1]-1)*TILE_DIMENSIONS[1],pygame.image.load(get_path("assets/head_up.png")).convert_alpha()]]
         
        # Spawn initial apple
        self.spawn_apple()
        
        # List of invalid directions
        # Guardrails to prevent you from dying by moving directly backwards into yourself
        self.dont_move_this_way = {pygame.K_LEFT: pygame.K_RIGHT, pygame.K_RIGHT: pygame.K_LEFT, pygame.K_UP: pygame.K_DOWN, pygame.K_DOWN: pygame.K_UP}
        # Initialize direction buffer
        # Stores a queue of the last 3 entered direction changes
        self.direction_buffer = [list(self.dont_move_this_way.keys())[random.randint(0,len(self.dont_move_this_way)-1)]]
        
        # Add extra initial body tiles to the snake
        for _ in range(max(3, INITIAL_SNAKE_LENGTH-1)):
            # Generate valid, random direction to move snake in initially
            direction = None
            while not direction or direction == self.dont_move_this_way[self.direction_buffer[-1]]: 
                direction = list(self.dont_move_this_way.keys())[random.randint(0,len(self.dont_move_this_way)-1)]
            
            self.direction_buffer.append(direction)             # Add direction to buffer
            self.move(static_growth=True)                                         # Move snake and repeat

        

    def move(self, static_growth: bool = False):
        """
        Moves the snake in a specified direction. \n
        Takes care of associated logic, such as collision detection, snake growth, etc.
        
        Args:
            static_growth (bool, optional): If True, the snake will grow without moving. Defaults to False.
        """
        global paused, background   # Load global variables

# -----> DEBUG PRINT
        # print(f"Entered move method. \t|\t Direction buffer: {list(pygame.key.name(direction) for direction in self.direction_buffer)} \t|\t Paused state: {paused}")
        
        head = self.body[0]
        newhead = [0,0,None]    # Initialize new head
        
        # Calculate coordinates of new head
        # ===========================================================================
        if self.direction_buffer[0] == pygame.K_LEFT:           # If moving left...
            if head[0] == 0:
                newhead = [WIDTH-TILE_DIMENSIONS[0], head[1]]   # Screen wrap movement
            else:
                newhead = [head[0]-TILE_DIMENSIONS[0], head[1]] # otherwise move nromally
        elif self.direction_buffer[0] == pygame.K_RIGHT:        # If moving right...
            if head[0] == WIDTH-TILE_DIMENSIONS[0]:
                newhead = [0, head[1]]                          # Screen wrap movement
            else:
                newhead = [head[0]+TILE_DIMENSIONS[0], head[1]] # otherwise move nromally
        elif self.direction_buffer[0] == pygame.K_UP:           # If moving up...
            if head[1] == 0:
                newhead = [head[0], HEIGHT-TILE_DIMENSIONS[1]]  # Screen wrap movement
            else:
                newhead = [head[0], head[1]-TILE_DIMENSIONS[1]] # otherwise move nromally
        elif self.direction_buffer[0] == pygame.K_DOWN:         # If moving down...
            if head[1] == HEIGHT-TILE_DIMENSIONS[1]:
                newhead = [head[0], 0]                          # Screen wrap movement
            else:
                newhead = [head[0], head[1]+TILE_DIMENSIONS[1]] # otherwise move nromally
        
        
        # Add extra frame if snake is about to collide with itself
        # ===========================================================================
        # There needs to be a check to prevent infinite extra frames, since this method is called 
        # once the extra frame wears off, in order to ascertain movement or death
        if paused[1] != "EXTRA FRAME LIFTED":   # Prevent infinite extra frames
            for tile in self.body[2:]:
                if newhead[0] == tile[0] and newhead[1] == tile[1]:
                    paused = [True, "EXTRA FRAME"]
        else:
            paused[1] = ""
        
        
        # Death check - Check if snake has collided with itself
        # ===========================================================================
        if not paused[0]:               # Skip death check if extra frame was just activated
            if newhead[:2] in [tile[:2] for tile in self.body[1:]]:  # ...otherwise check for death
                # Snake death animation:
                for _ in range(5):          # Blink snake body for 5 cycles upon death
                    for _,_,tile in self.body:
                        tile.set_alpha(0)
                        update_screen(snake=self, apple=self.apple)
                    pygame.time.delay(250)
                    for _,_,tile in self.body:
                        tile.set_alpha(255)
                        update_screen(snake=self, apple=self.apple)
                    pygame.time.delay(250)
                    
                # Then make snake body translucent
                for _,_,tile in self.body:
                    tile.set_alpha(128)
                    update_screen(snake=self, apple=self.apple)
                
                pygame.event.clear()        # Prevents instant restarts from queueing key press events during death animation
                paused = [True, "DEATH"]    # Pause the game due to death of snake
                
        
        # Tack on new head (for snake movement) & handle snake growth
        # ===========================================================================
        if not paused[0] or paused[1] == "START":   # Skip if extra frame was just actvated
                                                    # Do not skip if game is paused due to it having just started 
                                                    # (logic used when initially creating the snake)
            newhead.append(pygame.Surface(TILE_DIMENSIONS)) # Add surface to new head
            self.body.insert(0, newhead)                    # Add new head to body
            
            # Check if snake has eaten apple
            # ...if so, spawn new apple
            # ...if not, remove last body tile
            if newhead[0] == self.apple[0] and newhead[1] == self.apple[1]:
                self.spawn_apple()
            elif not static_growth:
                self.body.pop()
        
        # Apply assets to snake body
        # ===========================================================================
        if len(self.body) >= 3:      # Only necessary to apply assets once the snake has spawned
            self.apply_assets()
        
        # Reduce buffer
        # ===========================================================================
        if len(self.direction_buffer) > 1:
            self.direction_buffer.pop(0)
    
    def apply_assets(self) -> None:
        """
        Apply assets to all snake tiles
        """ 
        current_direction = self.direction_buffer[0]
        # Add asset for Head
        # ========================================================================
        head = self.body[0]
        if current_direction == pygame.K_LEFT:
            head[2] = pygame.image.load(get_path("assets/head_left.png")).convert_alpha()
        elif current_direction == pygame.K_RIGHT:
            head[2] = pygame.image.load(get_path("assets/head_right.png")).convert_alpha()
        elif current_direction == pygame.K_UP:
            head[2] = pygame.image.load(get_path("assets/head_up.png")).convert_alpha()
        elif current_direction == pygame.K_DOWN:
            head[2] = pygame.image.load(get_path("assets/head_down.png")).convert_alpha()
        head[2] = pygame.transform.scale(head[2], TILE_DIMENSIONS)
        
        
        headward_tile, current_tile = head, self.body[1]
        # Add assets for Body
        # ========================================================================
        # For headward tile --- current tile --- tailward tile, alter the texture on locations of headward tile and current tile
        for tailward_tile in self.body[2:]:
            
            # Straight-line body checks
            # ==========================
            if current_tile[0] == headward_tile[0] and current_tile[0] == tailward_tile[0]:   # Horizontal body
                current_tile[2] = pygame.image.load(get_path("assets/body_vertical.png"))
            elif current_tile[1] == headward_tile[1] and current_tile[1] == tailward_tile[1]:   # Vertical body
                current_tile[2] = pygame.image.load(get_path("assets/body_horizontal.png"))
            
            # Standard turn checks
            # ====================
            elif headward_tile[0] < current_tile[0]:         # headward tile is to the left of current tile
                if current_tile[1] < tailward_tile[1]:     # current tile is above tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
                elif current_tile[1] > tailward_tile[1]:    # current tile is below tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
            elif headward_tile[0] > current_tile[0]:        # headward tile is to the right of current tile
                if current_tile[1] < tailward_tile[1]:      # current tile is above tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                elif current_tile[1] > tailward_tile[1]:    # current tile is below tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
            elif headward_tile[1] < current_tile[1]:        # headward tile is above current tile
                if current_tile[0] < tailward_tile[0]:      # current tile is to the left of tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
                elif current_tile[0] > tailward_tile[0]:    # current tile is to the right of tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
            elif headward_tile[1] > current_tile[1]:        # headward tile is below current tile
                if current_tile[0] < tailward_tile[0]:      # current tile is to the left of tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                elif current_tile[0] > tailward_tile[0]:    # current tile is to the right of tailward tile
                    current_tile[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
            
            # Screen wrap turn checks
            # =======================
            # current tile on leftmost side of screen
            if current_tile[0] == 0:
                # headward tile on rightmost side of screen
                # aka left to right wrap
                if headward_tile[0] == WIDTH-TILE_DIMENSIONS[0]:
                    # current tile is above tailward tile
                    # aka up to left-right wrap
                    if current_tile[1] < tailward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
                    # current tile is below tailward tile
                    # aka down to left-right wrap
                    elif current_tile[1] > tailward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
                # headward tile on leftmost side of screen
                # aka right to left wrap
                elif tailward_tile[0] == WIDTH-TILE_DIMENSIONS[0]:
                    # current tile is above headward tile
                    # aka right-left wrap to down
                    if current_tile[1] < headward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
                    # current tile is below headward tile
                    # aka right-left wrap to up
                    elif current_tile[1] > headward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
            
            # current tile on rightmost side of screen
            elif current_tile[0] == WIDTH-TILE_DIMENSIONS[0]:
                # headward tile on leftmost side of screen
                # aka right to left wrap
                if headward_tile[0] == 0:
                    # current tile is above tailward tile
                    # aka up to right-left wrap
                    if current_tile[1] < tailward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                    # current tile is below tailward tile
                    # aka down to right-left wrap
                    elif current_tile[1] > tailward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
                # tailward tile on rightmost side of screen
                # aka left to right wrap
                elif tailward_tile[0] == 0:
                    # current tile is above headward tile
                    # aka left-right wrap to down
                    if current_tile[1] < headward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                    # current tile is below headward tile
                    # aka left-right wrap to up
                    elif current_tile[1] > headward_tile[1]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
            
            # current tile on topmost side of screen
            elif current_tile[1] == 0:
                # headward tile on bottommost side of screen
                # aka up to down wrap
                if headward_tile[1] == HEIGHT-TILE_DIMENSIONS[1]:
                    # current tile is to the left of tailward tile
                    # aka up-down wrap to right
                    if current_tile[0] < tailward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
                    # current tile is to the right of tailward tile
                    # aka up-down wrap to left
                    elif current_tile[0] > tailward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
                # tailward tile on topmost side of screen
                # aka down to up wrap
                elif tailward_tile[1] == HEIGHT-TILE_DIMENSIONS[1]:
                    # current tile is to the left of headward tile
                    # aka down-up wrap to right
                    if current_tile[0] < headward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topright.png")).convert_alpha()
                    # current tile is to the right of headward tile
                    # aka down-up wrap to left
                    elif current_tile[0] > headward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_topleft.png")).convert_alpha()
            
            # current tile on bottommost side of screen
            elif current_tile[1] == HEIGHT-TILE_DIMENSIONS[1]:
                # headward tile on topmost side of screen
                # aka down to up wrap
                if headward_tile[1] == 0:
                    # current tile is to the left of tailward tile
                    # aka down-up wrap to right
                    if current_tile[0] < tailward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                    # current tile is to the right of tailward tile
                    # aka down-up wrap to left
                    elif current_tile[0] > tailward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
                # tailward tile on bottommost side of screen
                # aka up to down wrap
                elif tailward_tile[1] == 0:
                    # current tile is to the left of headward tile
                    # aka up-down wrap to right
                    if current_tile[0] < headward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomright.png")).convert_alpha()
                    # current tile is to the right of headward tile
                    # aka up-down wrap to left
                    elif current_tile[0] > headward_tile[0]:
                        current_tile[2] = pygame.image.load(get_path("assets/body_bottomleft.png")).convert_alpha()
            current_tile[2] = pygame.transform.scale(current_tile[2], TILE_DIMENSIONS)
            headward_tile, current_tile = current_tile, tailward_tile
        
        # Add assets for Tail
        # =====================================================================
        # Check direction of tail w.r.t. second last tile and check for screen wrap
        # Important to ensure that screen is wrapping in the correct direction to prevent priority-based mapping issues
        tail, second_last_tile = self.body[-1], self.body[-2]
        left_to_right_wrap_flag = tail[0] == 0 and second_last_tile[0] == WIDTH-TILE_DIMENSIONS[0]
        right_to_left_wrap_flag = tail[0] == WIDTH-TILE_DIMENSIONS[0] and second_last_tile[0] == 0
        top_to_bottom_wrap_flag = tail[1] == 0 and second_last_tile[1] == HEIGHT-TILE_DIMENSIONS[1]
        bottom_to_top_wrap_flag = tail[1] == HEIGHT-TILE_DIMENSIONS[1] and second_last_tile[1] == 0
        if (tail[0] < second_last_tile[0] and not left_to_right_wrap_flag) or right_to_left_wrap_flag:     # Tail is to the left of the body
            tail[2] = pygame.image.load(get_path("assets/tail_left.png")).convert_alpha()
        elif (tail[0] > second_last_tile[0] and not right_to_left_wrap_flag) or left_to_right_wrap_flag:     # Tail is to the right of the body
            tail[2] = pygame.image.load(get_path("assets/tail_right.png")).convert_alpha()
        elif (tail[1] < second_last_tile[1] and not top_to_bottom_wrap_flag) or bottom_to_top_wrap_flag:     # Tail is above the body
            tail[2] = pygame.image.load(get_path("assets/tail_up.png")).convert_alpha()
        elif (tail[1] > second_last_tile[1] and not bottom_to_top_wrap_flag) or top_to_bottom_wrap_flag:     # Tail is below the body
            tail[2] = pygame.image.load(get_path("assets/tail_down.png")).convert_alpha()
        tail[2] = pygame.transform.scale(tail[2], TILE_DIMENSIONS)
    
    def spawn_apple(self):
        """
        Spawns an apple object on a random position on the board. \n
        Apple object is stored as a list field of the snake object in the form of [x, y, Surface]"""
        # Find valid coordinates to spawn apple
        snake_coords = [tile[:2] for tile in self.body[1:]]             # List of coordinates of tiles of the snake body
        good_coordinates_flag = False
        while not good_coordinates_flag:
            x, y = random.randint(0, GRID_SIZE[0]-1)*TILE_DIMENSIONS[0], random.randint(0, GRID_SIZE[1]-1)*TILE_DIMENSIONS[1]
            good_coordinates_flag = not [x,y] in snake_coords
        
        # Spawn apple
        self.apple = [x, y, pygame.image.load(get_path("assets/apple.png")).convert_alpha()]
        self.apple[2] = pygame.transform.scale(self.apple[2], TILE_DIMENSIONS)
        
# -----> DEBUG PRINT
        # print(f"Apple spawned at: {apple[0]/TILE_DIMENSIONS[0]},{apple[1]/TILE_DIMENSIONS[1]}", end="\r")


def update_screen(*args: tuple, snake: Snake, apple: list) -> None:
    """
    Draws objects to the screen and updates it

    Args:
        *args (tuple): Additional objects to be drawn to screen.\n
                       Objects must be in the form of (Surface, x, y)
        snake (Snake): Snake object.
        apple (list): Apple object.
    """
    global background   # Load background
    
    # Refill background
    background.fill(DARK_GREEN) # Sets background color

    # Draw grid
    bgTile = pygame.image.load(get_path("assets/tile.png")).convert_alpha()
    for row in range(TILE_DIMENSIONS[1]):
        for tile in range(TILE_DIMENSIONS[0]):
            background.blit(bgTile, (tile * TILE_DIMENSIONS[0], row * TILE_DIMENSIONS[1]))
    
    # Draw snake
    for tile in snake.body:
        background.blit(tile[2],(tile[0], tile[1]))
    
    # Draw apple
    background.blit(apple[2],(apple[0], apple[1]))
    
    # Update score counter
    score_font = pygame.font.Font(None, 36) # Font object for score
    score_counter = score_font.render(f"{len(snake.body)-1-INITIAL_SNAKE_LENGTH}", 1, (255, 255, 255))
    background.blit(score_counter, (WIDTH/2, TILE_DIMENSIONS[1]/2))
    
    # Draw other objects
    for arg in args:
        background.blit(arg[0],(arg[1], arg[2]))
    
    # Update screen
    pygame.display.update()

def keyboard_inputs():
    pass
    # For future code cleanup purposes




def main():
    """
    ### Main loop: Run upon execution. \n
    Initializes board, variables and begins pygame window-loop.
    """
    global paused, background   # Load global variables
    snake = Snake()             # Create snake
    
    pygame.init()               # Initializes pygame module
    pygame.display.set_caption("Snake") # Sets window title
    pygame.display.set_icon(pygame.image.load(get_path("assets/head_up.png"))) # Sets window icon (in the top-left corner of the window)
    clock = pygame.time.Clock() # Create FPS object
    loop_ctr = 1                # Loop counter variable
    win_restart_key_ctr = 0     # Key press counter to restart on win
    
    while True:
        """
        Pygame window-loop. Exits upon closing the window
        """
        
        # Event checking
        # ===========================================================================
        event_list = pygame.event.get()     # Gets a list of all events
        
        for event in event_list:            # Always check for if X is clicked
            if event.type == QUIT:          # Event for if X is clicked
                pygame.quit()               # Closes window
                sys.exit()                  # Exits program
        
        # If game is not paused...
        if not paused[0]:                   
            for event in event_list:        # Begin parsing events
                if event.type == pygame.KEYDOWN:    # If a key is pressed
                    # If pressed key is a valid direction, add to movement buffer
                    # ... w/ guard-rails so you can't die by moving directly backwards into yourself
                    if event.key in snake.dont_move_this_way.keys() and snake.dont_move_this_way[event.key] != snake.direction_buffer[-1]:
                        # Add key to buffer if buffer is not full
                        if len(snake.direction_buffer) < DIRECTION_BUFFER_LENGTH:
                            snake.direction_buffer.append(event.key)
                        # If buffer is full, overwrite most recent key
                        elif event.key != snake.dont_move_this_way[snake.direction_buffer[-2]]:
                            snake.direction_buffer[-1] = event.key
                    
                    # Pause when ESC is pressed
                    if event.key == pygame.K_ESCAPE:
                        paused = [True, "PAUSE"]
        
        # If game is paused...
        else:
            if paused[1] in ("PAUSE", "START"):     # When paused before game has begun...
                for _,_,tile in snake.body:         # Turn tiles translucent
                    tile.set_alpha(128)
                
                for event in event_list:            # Unpause after delay when any key is pressed
                    if event.type == pygame.KEYDOWN:
                        for i in range(PAUSE_DELAY):    # Aforementioned delay
                            if i%10**3 == 0:
                                # Display time remaining until unpausing
                                pause_font = pygame.font.Font(None, 36) # Font object for pause message
                                text_pause = pause_font.render(f"{round(floor(PAUSE_DELAY/10**3) - i/10**3)}", 1, (255, 255, 255))
                                update_screen((text_pause, WIDTH/2, HEIGHT/2),snake=snake, apple=snake.apple)
                            pygame.time.wait(1)
                        
                        
                        for _,_,tile in snake.body: # Return opacity back to tiles once unpaused
                            tile.set_alpha(255)
                            
                        # Update move direction when unpausing <----- POTENTIAL LIFEHACK 👀
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                            snake.direction_buffer[0] = event.key
                            
                        # Finally, unpause
                        paused = [False,""]
                
            elif paused[1] == "EXTRA FRAME":        # When paused for extra frames...
                pygame.time.wait(EXTRA_FRAMES)      # Wait for given amount of time
                
                paused = [False,"EXTRA FRAME LIFTED"]   # Unpause now that extra frame has been executed

                        
            elif paused[1] == "DEATH":              # When paused due to snake death...
                for event in event_list:
                    if event.type == pygame.KEYDOWN:
                        # Restarts game when any key is pressed
                        paused = [True, "START"]
                        snake = Snake()
                        loop_ctr = 1
                    
            elif paused[1] == "WIN":
                win_font = pygame.font.Font(None, 36) # Font object for pause message
                text_win_1 = win_font.render(f"You Win! =D", 1, (255, 255, 255))
                text_win_2 = win_font.render(f"Press ESC 3x to restart!", 1, (255, 255, 255))
                update_screen((text_win_1, WIDTH/2-text_win_1.get_width()/2, HEIGHT/2 ), (text_win_2, WIDTH/2-text_win_2.get_width()/2, HEIGHT/2+text_win_1.get_height()),snake=snake, apple=snake.apple)
                
                for event in event_list:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            win_restart_key_ctr += 1
                        
                # Restarts game when conditions are met
                if win_restart_key_ctr == 3:
                    paused = [True, "START"]
                    snake = Snake()
                    loop_ctr = 1
                    win_restart_key_ctr = 0
                
                continue
        
        # Move snake head every time loop_ctr has reset
        # ===========================================================================
        if loop_ctr == 1 and not paused[0]:
            snake.move()
        
        # Win condition check
        # ===========================================================================
        if len(snake.body) - 1 - INITIAL_SNAKE_LENGTH == WIN_SCORE_THRESHOLD:
            paused = [True, "WIN"]
        
# -----> DEBUG PRINT
        # print(f"Main method ticked. \t|\t Direction buffer: {list(pygame.key.name(direction) for direction in snake.direction_buffer)} \t|\t Paused state: {paused} \t|\t Loop counter: {loop_ctr}")
        
        # TODO
        # Add apple-bag power-up

        # Update screen
        # ===========================================================================
        update_screen(snake=snake, apple=snake.apple)
        
        # Game loop
        # ===========================================================================
        clock.tick(FPS)                     # Ensures a max of 60 FPS
        if loop_ctr % (LOOP_DELAY) == 0:    # Increment loop counter
            loop_ctr = 1
        else:
            loop_ctr += 1



if __name__ == "__main__":
    main() # Godspeed 🫡