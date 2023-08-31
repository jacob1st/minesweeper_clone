import pygame

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

