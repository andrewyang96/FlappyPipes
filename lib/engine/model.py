##############################################################################
# model.py
##############################################################################
# State-based model that interpets input and generates events to alert views
# to changes.
##############################################################################
# 06/12 - Flembobs
##############################################################################

class Model:
   
    @classmethod
    def change_state(self, new_state):
        # print 'change model to', new_state # DEBUG
        self.state = new_state                                
                                 
##############################################################################
# GAME OBJECT
##############################################################################

class GameObject:
   
    def render(self, screen):
        raise NotImplementedError
      
##############################################################################
# STATE
##############################################################################

class State:
    def __init__(self, systemeventlistener, guieventlistener):
        systemeventlistener.__init__(self)
        guieventlistener.__init__(self)
        self.game_objects = []
