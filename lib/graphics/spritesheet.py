# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)
 
import pygame, sys
 
class Spritesheet(object):
    def __init__(self, filename):
        """
        Initialize a spritesheet.
        filename - Filename of the sprite sheet.
        """
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message
    
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        """
        Loads image from a specific rectangle on the spritesheet.
        rectangle - The specified rectangle: Rect(x,y,x+offset,y+offset)
        """
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        """
        Loads multiple images.
        rects - A list of rectangles, each: Rect(x,y,x+offset,y+offset)
        """
        return [self.image_at(rect, colorkey) for rect in rects]
    
    # Load a whole strip of images (Used for SpriteSheetAnim)
    def load_strip(self, rect, image_count, colorkey = None):
        """
        Loads a strip of images and returns them as a list
        """
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

# CONSTANTS
from pygame.locals import Rect
SS_NAME = '\\lib\\graphics\\spritesheet.png'
RECT_DICT = {'background':Rect(5,5,144,256), # background
             'pause':Rect(159,5,13,14), # square pause button
             'resume':Rect(182,5,13,14), # square resume button
             'start':Rect(205,5,40,14), # long start button
             'ok':Rect(159,29,40,14), # long restart (OK) button
             'fb1':Rect(255,5,17,12), # flappy bird 1
             'fb2':Rect(255,27,17,12), # flappy bird 2
             'fb3':Rect(209,49,17,12), # flappy bird 3
             'logo':Rect(159,71,106,22), # flappy pipes logo
             'gameover':Rect(159,103,94,19), # game over logo
             'getready':Rect(159,132,87,22), # get ready logo
             'bronze':Rect(263,103,22,22), # bronze medal
             'gold':Rect(256,135,22,22), # gold medal
             'platinum':Rect(159,167,22,22), # platinum medal
             'silver':Rect(191,167,22,22), # silver medal
             'instructions':Rect(223,167,49,49), # instructions
             'player':Rect(159,226,42,26), # pipe player
             'scorebg':Rect(282,5,113,58), # scoreboard
             'terrain':Rect(211,226,154,52), # terrain
             }

# TEST CASE
if __name__ == '__main__':
    SS_NAME = 'spritesheet.png'
    from pygame.locals import *  # @UnusedWildImport
    pygame.init()
    clock = pygame.time.Clock()
    framerate = 60
    # screen = pygame.display.set_mode((288,256))
    screen = pygame.display.set_mode((576,512))
    ss = Spritesheet(SS_NAME)
    colorkey = False
    
    # extract sprites
    imgs = ss.images_at(RECT_DICT.values(), colorkey)
    index = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    index += 1
                if event.key == K_LEFT:
                    index -= 1
                index = index % len(imgs)
        screen.fill((255,0,0))
        
#         screen.blit(imgs[index], (0,0))
        screen.blit(pygame.transform.scale2x(imgs[index]),
                    (0,0)) # smooth scale
        
        pygame.display.flip()
        clock.tick(framerate)