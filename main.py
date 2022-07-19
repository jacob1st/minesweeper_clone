import math
import pygame
import random
import time

class Board:
    def __init__(self, x, y, size, row, column, bomb_num):
        # Takes in starting values and coordinates, generates board
        self.x = x
        self.y = y
        self.row = row
        self.column = column
        self.bomb_num = bomb_num
        self.bomb_pos = []
        self.tiles = []
        self.hitboxes = []
        self.grouped_zeros = []
        self.gameover = "n"
        self.size = size
        self.generate_board(x, y)

    def generate_board(self, x, y):
        # Creates a 2d list filled with Tile objects, keeps track of hitboxes in a 1d list
        starting_y = y
        for col in range(self.column):
            rows = []
            for row in range(self.row):
                rows.append(Tile([x, y], self.size, -2))
                self.hitboxes.append(pygame.Rect(x, y, self.size, self.size))
                y += self.size

            self.tiles.append(rows)
            x += self.size
            y = starting_y

        # Generates the correct numbers for tiles
        self.generate_bombs()
        self.generate_values()

        # Seperates connecting zeroes into connected groups
        self.neighboring_zeroes()

    def generate_bombs(self):
        # Assign a specific number of randomly selected squares to be bombs
        while len(self.bomb_pos) < self.bomb_num:
            row = random.randint(0, self.row - 1)
            col = random.randint(0, self.column - 1)
            if (col, row) not in self.bomb_pos:
                self.tiles[col][row].value = -1
                self.bomb_pos.append((col, row))

    def generate_values(self):
        # Each square has a value based on how many bombs it touches
        for col in range(len(self.tiles)):
            for row in range(len(self.tiles[col])):
                if self.tiles[col][row].value != -1:
                    value = 0
                    for i in self.get_neighbors(col, row):
                        if self.tiles[i[0]][i[1]].value == -1:
                            value += 1
                    self.tiles[col][row].value = value

    def get_neighbors(self, x, y):
        # Returns a list of positions for all touching squares
        neighbors = []
        # Top
        if y > 0:
            neighbors.append([x, y - 1])
        # Bottom
        if y < self.row - 1:
            neighbors.append([x, y + 1])
        # Left
        if x > 0:
            neighbors.append([x - 1, y])
        # Right
        if x < self.column - 1:
            neighbors.append([x + 1, y])
        # Top Right
        if x < self.column - 1 and y > 0:
            neighbors.append([x + 1, y - 1])
        # Top Left
        if x > 0 and y > 0:
            neighbors.append([x - 1, y - 1])
        # Bottom Right
        if x < self.column - 1 and y < self.row - 1:
            neighbors.append([x + 1, y + 1])
        # Bottom Left
        if x > 0 and y < self.row - 1:
            neighbors.append([x - 1, y + 1])
        
        return neighbors

    def neighboring_zeroes(self):
        # Goes through each square and runs a check on its neighbors to find touching zeroes. All touching zeroes will have the same group number
        group = 0
        for col in range(len(self.tiles)):
            for row in range(len(self.tiles[col])):
                if self.tiles[col][row].value == 0 and self.tiles[col][row].tested == False:
                    self.check_neighbors([col, row], group)
                    group += 1

    def check_neighbors(self, pos, group_num):
        # Recursively check any neighboring zero squares for their neighboring zero squares
        self.tiles[pos[0]][pos[1]].group(group_num)
        for i in self.get_neighbors(pos[0], pos[1]):
            if self.tiles[i[0]][i[1]].value == 0 and self.tiles[i[0]][i[1]].tested == False:
                self.check_neighbors(i, group_num)                

    def tile_hit(self, pos):
        # Handles the clicking of a square
        # Does nothing if the game is over
        # If the tile is a zero, opens up all touching zeroes and bordering squares (unless flagged)
        # If the tile is a normal value it reveals it 
        # If the tile is a bomb all bombs are revealed and the game ends
        # After clicking a tile, check to see if all tiles are revealed and you win

        if self.gameover != 'n':
            return 0
        tile = self.tiles[pos[0]][pos[1]]

        if tile.flagged: # UNSURE WHETHER TO KEEP THIS
            return 0

        if tile.value == 0:
            for t in self.get_neighbors(pos[0], pos[1]): # Reveal all neighboring numbers
                if self.tiles[t[0]][t[1]].value != 0:
                    self.tiles[t[0]][t[1]].revealed = True

            tile.revealed = True
            tile.flagged = False

            tile_group = tile.group_num
            for col in range(len(self.tiles)):
                for row in range(len(self.tiles[col])):
                    if self.tiles[col][row].value == 0 and self.tiles[col][row].group_num == tile_group: # Reveal any zero that is part of the same group
                        self.tiles[col][row].revealed = True
                        for t in self.get_neighbors(col, row): # Reveal surrounding numbers to those zeroes
                            if self.tiles[t[0]][t[1]].value != 0:
                                self.tiles[t[0]][t[1]].revealed = True

        elif tile.value == -1: # Hit a bomb
            self.gameover = 'l'
            for i in self.bomb_pos:
                self.tiles[i[0]][i[1]].flagged = False
                self.tiles[i[0]][i[1]].revealed = True
        else: # Hit a normal number
            tile.revealed = True
            tile.flagged = False

        self.check_win()

    def flag_tile(self, pos):
        # Flags a tile if it is not already revealed, unflags an already flagged tile
        # Returns a number to keep track of how many bombs you've guessed so far
        if self.gameover != 'n':
            return 0
        bombs_left = 0
        if self.tiles[pos[0]][pos[1]].flagged:
            self.tiles[pos[0]][pos[1]].flagged = False
            self.tiles[pos[0]][pos[1]].revealed = False
            bombs_left = -1
        elif self.tiles[pos[0]][pos[1]].revealed == False:
            self.tiles[pos[0]][pos[1]].flagged = True
            bombs_left = 1

        self.check_win()
        
        return bombs_left

    def reset(self):
        # Resets the board and regenerates
        self.bomb_pos = []
        self.tiles = []
        self.hitboxes = []
        self.grouped_zeros = []
        self.gameover = "n"
        self.generate_board(self.x, self.y)

    def check_win(self):
        # See if all tiles that should be revealed are, every tile minus the bombs should be revealed to win
        count = 0
        for tiles in self.tiles:
            for tile in tiles:
                if tile.revealed == True and tile.flagged == False and tile.value != -1:
                    count += 1

        if count + self.bomb_num == self.row * self.column:
            self.gameover = "w" 

    def draw(self, display):
        # Display all the tiles
        for col in range(len(self.tiles)):
            for row in range(len(self.tiles[col])):
                self.tiles[col][row].draw(display)       
                

class Tile:
    def __init__(self, pos, size, value):
        # Keeps track of x, y position on screen, not position on board
        self.pos = pos
        self.size = size
        self.value = value
        self.group_num = -1
        self.tested = False
        self.flagged = False
        self.revealed = False
        self.number_pic = {0: 'images/pressed.png',
                    1: 'images/one.png', 
                    2: 'images/two.png',
                    3: 'images/three.png', 
                    4: 'images/four.png', 
                    5: 'images/five.png', 
                    6: 'images/six.png', 
                    7: 'images/seven.png', 
                    8: 'images/eight.png',
                    -1: 'images/bomb.png'}

    def draw(self, display):
        # Draws the tile, flagged tiles are not revealed.
        if self.flagged:
            flagged_image = pygame.image.load('images/flagged.png')
            flagged_image = pygame.transform.scale(flagged_image, (self.size, self.size))
            display.blit(flagged_image, (self.pos[0], self.pos[1]))
            # pygame.draw.rect(display, (255, 0, 0), pygame.Rect(self.pos[0], self.pos[1], self.size, self.size), 2)
            # square_value = score_font.render("?", 1, (0, 0, 0))
            # display.blit(square_value, (self.pos[0] + self.size/2, self.pos[1] + self.size/2))
        elif self.revealed:
            block = pygame.image.load(self.number_pic[self.value])
            block = pygame.transform.scale(block, (self.size, self.size))
            display.blit(block, (self.pos[0], self.pos[1]))
        else:
            button_image = pygame.image.load('images/block.png')
            button_image = pygame.transform.scale(button_image, (self.size, self.size))
            display.blit(button_image, (self.pos[0], self.pos[1]))
            # pygame.draw.rect(display, (255, 0, 0), pygame.Rect(self.pos[0], self.pos[1], self.size, self.size), 2)

    def group(self, num):
        self.tested = True
        self.group_num = num


# Draw the board and write everything, update display
def draw_screen(display):
    display.fill((208, 208, 208))
    my_board.draw(display)
    bombs_left = score_font.render(str(my_board.bomb_num - bombs_guessed[0]), 1, (0, 0, 0))
    display.blit(bombs_left, (50, 50))

    if my_board.gameover == "w":
        game_status = "You WON!"
    elif my_board.gameover == "l":
        game_status = "You Lost"
    else:
        game_status = "Minesweeper"

    if len(starting_time) == 1:
        display_timer = score_font.render(str(round(time.time() - starting_time[0])), 1, (0, 0, 0))
        display.blit(display_timer, (300, 50))
    else:
        display_timer = score_font.render(str(starting_time[1]), 1, (0, 0, 0))
        display.blit(display_timer, (300, 50))

    controls = score_font.render("Shortcuts: 'r' - resets board,     's' - shows board,     'c' - chooses one blank space for you", 1, (0, 0, 0))
    display.blit(controls, (400, 20))


    display_status = score_font.render(game_status, 1, (0, 0, 0))
    display.blit(display_status, (100, 50))

    pygame.display.update()

# Hitboxes are kept in a 1d line so it's easier to loop, this checks a point (mouse pos) to see if it lands on a tile
def check_for_collision(pos):
    for i in range(len(my_board.hitboxes)):
        if my_board.hitboxes[i].collidepoint(pos):
            return i
    else:
        return -1

# Converts a pos from a 1d list (hitbox) to where it would fall on the board. (Read columns top to bottom and rows left to right)
# e.x. If you had a 10x10 grid, the 13th block would be the second column, 3 down
def pos_to_xy(pos, rows, columns):
    col = math.floor(pos/rows)

    if col == 0:
        row = pos % (columns)
    else:
        row = pos % (col * rows)
    
    return (col, row)

# Take the mouse press and see if it collides with a block, left click reveals blocks, right click flags them
def handle_mouse_click(mouse_button):
    mouse_position = pygame.mouse.get_pos()
    collide_block = check_for_collision(mouse_position)
    if collide_block > -1:
        pos_of_collision = pos_to_xy(collide_block, ROWS, COLUMNS)

        if mouse_button == 1:
            my_board.tile_hit(pos_of_collision)
        elif mouse_button == 3:
            bombs_guessed[0] += my_board.flag_tile(pos_of_collision)
    

# Constant values, change these for different levels

WIDTH = 1000
HEIGHT = 700

ROWS = 15
COLUMNS = 20
BLOCK_SIZE = 30
GRID_X = 100
GRID_Y = 100
NUMBER_OF_BOMBS = 50

# WIDTH = 700
# HEIGHT = 700

# ROWS = 10
# COLUMNS = 10
# BLOCK_SIZE = 50
# GRID_X = 100
# GRID_Y = 100
# NUMBER_OF_BOMBS = 10

my_board = Board(GRID_X, GRID_Y, BLOCK_SIZE, ROWS, COLUMNS, NUMBER_OF_BOMBS)

# Initialize pygame screen, clock, and a font
pygame.init()
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")
clock = pygame.time.Clock()
score_font = pygame.font.SysFont("Arial", int(BLOCK_SIZE/2))

# Keep track of guessed bombs so far
bombs_guessed = [0]

# Timer
starting_time = [time.time()]


# Main Game loop, handles clicks of mouse and keys, draws the screen
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN: # If mouse is clicked
            handle_mouse_click(event.button)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        bombs_guessed[0] = 0
        starting_time = [time.time()]
        my_board.reset()
    if keys[pygame.K_s]:
        for tiles in my_board.tiles:
            for tile in tiles:
                tile.flagged = False
                tile.revealed = True
        my_board.gameover = "l"
    
    if my_board.gameover != "n":
        starting_time.append(round(time.time() - starting_time[0]))


    #####
    if keys[pygame.K_c]:
        while True:
            col = random.randint(0, my_board.column - 1)
            row = random.randint(0, my_board.row - 1)
            if my_board.tiles[col][row].value == 0:
                my_board.tile_hit([col, row])
                break
    #####
    
    draw_screen(display)