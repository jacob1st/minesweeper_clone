import pygame
import random

from tile import Tile

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
                
