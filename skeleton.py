##############################################################################
# skeleton.py
##############################################################################
# Main script to launch game.  Creates the model, views and controllers.
##############################################################################
# 03/13 - Flembobs
##############################################################################

import pygame

from lib.engine.systemevents import SystemEventManager  # @UnusedImport

# controllers
from lib.engine.cpuspinner import CPUSpinner
from lib.engine.pygameeventsmanager import PygameEventsManager

# model
from lib.engine.model import Model

# views
from lib.engine.pygameview import PygameView

# initial state
from lib.gamestate import IntroState

##############################################################################
# CONSTANTS
##############################################################################

GAME_NAME = "Flappy Pipes"
FPS = 60
SCREEN_SIZE = (576, 512)
BG_COLOR = (0, 0, 0)

##############################################################################
# GAME ENGINE CLASS
##############################################################################

class GameEngine:
    
    def __init__(self):
        # print 'gameengine init' # DEBUG
        # initialize pygame environment
        pygame.init()
        
        # create controllers
        self.cpu_spinner = CPUSpinner(FPS) # regulate frame speed
        self.pygame_events_manager = PygameEventsManager() # translate keyboard inputs to Events
        
        # create views
        self.pygame_view = PygameView(GAME_NAME, SCREEN_SIZE, BG_COLOR) # create screen
        
        # init model
        Model.change_state(IntroState(SCREEN_SIZE)) # establish GameState, which is a derived class of State, as the current state
        
        
    #--------------------------------------------------------------------------
    
    def start(self):
        # print 'self.cpu_spinner.run()' # DEBUG
        # start the cpu spinner
        self.cpu_spinner.run()
        
    
    
##############################################################################
# MAIN EXECUTION
##############################################################################

gameEngine = GameEngine()
# print 'gameEngine.start()' # DEBUG
gameEngine.start()
pygame.quit()
