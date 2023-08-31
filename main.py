import math
import pygame
import random
import time

from board import Board

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
