##############################################################################
# gui.py
##############################################################################
# A collection of classes used to create a menu system within the game.
##############################################################################
# 03/13 - Flembobs
##############################################################################

import pygame

from engine.events import *  # @UnusedWildImport
from engine.systemevents import *  # @UnusedWildImport
from engine.model import GameObject
from weakref import WeakKeyDictionary  # @Reimport

##############################################################################
# CONSTANTS
##############################################################################

# Text input box ignores these keys so unprintable characters aren't input
TEXT_BOX_IGNORE = [pygame.K_TAB, pygame.K_CLEAR, pygame.K_RETURN,
                   pygame.K_PAUSE]

##############################################################################
# GUI EVENTS
##############################################################################

class ButtonClickedEvent(Event):
    """
    Posted by a button when it is clicked.
    """
    
    def __init__(self, button):
        """
        button - reference to the button that was clicked
        """
        self.button = button
        
class ButtonMouseOverEvent(Event):
    """
    Posted by a button when the mouse enters its rect.
    """
    
    def __init__(self, button):
        """
        button - reference to the button that was mouse overed.
        """                                                    
        self.button = button

class FadeIntoGameEvent(Event):
    """
    Posted by start button when game should be faded into.
    """
    
    def __init__(self):
        pass

##############################################################################
# GUI EVENT MANAGER
##############################################################################

class GUIEventManager(EventManager):
    listeners = WeakKeyDictionary()
   
##############################################################################
# GUI EVENT LISTENER
##############################################################################

class GUIEventListener(Listener):
   
    def __init__(self):
        """
        Creates a System Event Listener that will register itself with the
        GUI Event Manager.
        """
        Listener.__init__(self, GUIEventManager)  
   
##############################################################################
# COMPONENTS - IMAGE
##############################################################################

class Image(GameObject):
    """
    Used to display an image on screen as part of the GUI.  Inherits Game
    Object so that it can easily be rendered on screen.
    """

    def __init__(self, rect, surf):
        self.rect = rect
        self.surf = surf
      
    def render(self, screen):
        screen.blit(self.surf, self.rect)

##############################################################################
# COMPONENTS - BUTTON
##############################################################################

class Button(Image, SystemEventListener):
    """
    Inherits the Image class so that it can be drawn on screen.  Listens to
    the system event manager for relevant mouse events.
    """

    def __init__(self, rect, normal_surf, mouse_over_surf=None):
   
        SystemEventListener.__init__(self)
        Image.__init__(self, rect, normal_surf)
   
        self.normal_surf = normal_surf
        self.mouse_over_surf = mouse_over_surf
      
        # is true if the mouse is within the button's rect
        self._mouse_over = False
    
    #--------------------------------------------------------------------------
    
    def notify(self, event):
    
        # check for mouse over
        if isinstance(event, MouseMotionEvent):
         
            # ignore if there is no mouse over surf
            if self.mouse_over_surf is None:
                return      
            
            # check for collision
            if self.rect.collidepoint(event.pos):
            
                # test if we need to post a mouse over event
                if not self._mouse_over:
                    self._mouse_over = True
                    GUIEventManager.post(ButtonMouseOverEvent(self))
            
                # change the surf to the mouse over surf
                if self.mouse_over_surf is not None:
                    self.surf = self.mouse_over_surf
         
            # mouse not within button bounds
            else:
                self._mouse_over = False
                self.surf = self.normal_surf
            
        # check for mouse click
        if isinstance(event, MouseButtonEvent):
            
            if event.type == pygame.MOUSEBUTTONDOWN and \
                event.button == 1 and \
                self.rect.collidepoint(event.pos):
                
                GUIEventManager.post(ButtonClickedEvent(self))
            
##############################################################################
# COMPONENTS - TEXT
##############################################################################

class Text(Image):
    """
    Allows a string to be displayed on screen.
    """
    
    def __init__(self, text, color, fontsize, font='courier', is_sys_font=False):
        """
        text - the text to be displayed
        colour - the colour the text should be drawn
        """
        self.color = color
        self.fontsize = fontsize
        self.font = font
        self.is_sys_font = is_sys_font
        if self.is_sys_font:
            text_surf = pygame.font.SysFont(font, fontsize, True).\
                                            render(text, True, color)
        else:
            text_surf = pygame.font.Font(font, fontsize).render(text, True, color)
                            
        text_rect = pygame.Rect((0, 0), (text_surf.get_width(),
                                text_surf.get_height()))
                                       
        Image.__init__(self, text_rect, text_surf)
    
    def update(self, text):
        if self.is_sys_font:
            self.surf = pygame.font.SysFont(self.font, self.fontsize, True).\
                                            render(text, True, self.color)
        else:
            self.surf = pygame.font.Font(self.font, self.fontsize).render(text, True, self.color)
        self.rect = pygame.Rect((0, 0), (self.surf.get_width(),
                                self.surf.get_height()))

class RotatingText(Text, SystemEventListener):
    """
    Allows a rotating and resizable string to be displayed.
    """
    def __init__(self, text, color, fontsize, rotation_speed=0, initial_size=1.0, growth_rate=0.0):
        """
        text - the text to be displayed
        colour - the colour the text should be drawn
        """
        Text.__init__(self, text, color, fontsize)
        SystemEventListener.__init__(self)
        self.orig_rect = self.rect.copy()
        self.orig_surf = self.surf.copy()
        self.angle = 0
        self.rotation_speed = rotation_speed
        self.size = initial_size
        self.growth_rate = growth_rate
    
    def notify(self, event):
        if isinstance(event, TickEvent):
            self.angle += self.rotation_speed
            self.size += self.growth_rate
            self.rotate_center()
    
    def rotate_center(self):
        self.surf = pygame.transform.rotozoom(self.orig_surf, self.angle, self.size)
        self.rect = self.surf.get_rect(center=self.orig_rect.center)

class FadeScreen(Image, SystemEventListener):
    """
    Fade-out/fade-in screen.
    """
    def __init__(self, speed, starting_alpha, screensize, color=(0,0,0)):
        SystemEventListener.__init__(self)
        Image.__init__(self, pygame.Rect((0,0),screensize), pygame.Surface(screensize))
        self.speed = speed
        self.surf.set_alpha(starting_alpha)
        self.surf.fill(color)
        self.event, self.alpha_trigger = None, None
    
    def notify(self, event):
        if isinstance(event, TickEvent):
            self.change_alpha(self.speed)
            if self.surf.get_alpha() < 0:
                self.set_alpha(0)
            elif self.surf.get_alpha() > 255:
                self.set_alpha(0)
            if self.get_alpha() == self.alpha_trigger:
                SystemEventManager.post(FadeIntoGameEvent())
    
    def change_alpha(self, delta):
        self.surf.set_alpha(self.surf.get_alpha() + delta)
    
    def set_alpha(self, alpha):
        self.surf.set_alpha(alpha)
    
    def get_alpha(self):
        return self.surf.get_alpha()
    
    def set_color(self, color):
        self.surf.fill(color)
    
    def set_speed(self, speed):
        self.speed = speed
    
    def set_end_event(self, alpha_trigger, event):
        self.event = event
        self.alpha_trigger = alpha_trigger
    
    def delete_end_event(self):
        self.event, self.alpha_trigger = None, None
      
##############################################################################
# COMPONENTS - TEXT INPUT BOX
##############################################################################

class TextInputBox(Image, SystemEventListener):
    """
    Provides a box which the user can use to input text.
    """                                               
   
    def __init__(self, topleft, width, initial_text, fg_color, bg_color, fontsize,
                 border_width=2):
                
        SystemEventListener.__init__(self)
                
        # text to be displayed in the box
        self.text = initial_text
      
        # size of text within the box
        self.fontsize = fontsize
      
        # save the colours used
        self.fg_color = fg_color
        self.bg_color = bg_color
      
        # save border width
        self.border_width = border_width
   
        # boolean indicating if the text box has focus
        self.has_focus = False
      
        # flag used to record the first click so that initial text is deleted
        self._first_focus = True
      
        # time until the next cursor flash
        self._cursor_flash_time = 0
      
        # whether or not the cursor should be drawn
        self._cursor_toggle = True
      
        # number of frames between each cursor flash
        self._FRAMES_BETWEEN_FLASHES = 30
      
        # width of cursor
        self._CURSOR_WIDTH = 3
      
        # create the surface and rect for the box      
        box_surf = self._create_box(width, fg_color, bg_color,
                                  fontsize, border_width)
      
        box_rect = pygame.Rect(topleft, (box_surf.get_width(),
                                         box_surf.get_height()))                               
   
        # initialize the image with the box rect and surf
        Image.__init__(self, box_rect, box_surf)
      
    #--------------------------------------------------------------------------
   
    def notify(self, event):
      
        if isinstance(event, MouseButtonEvent):
         
            # check if click is within bounds of the box
            if event.type == pygame.MOUSEBUTTONDOWN and \
                event.button == 1:
            
                if self.rect.collidepoint(event.pos):
            
                    self.has_focus = True
            
                    # erase initial text on first focus
                    if self._first_focus:
                        self.text = ""
                        self._first_focus = False
            
                else:
                    self.has_focus = False
               
        if isinstance(event, KeyboardEvent):
         
            if not self.has_focus:
                return
            
            if event.type is not pygame.KEYDOWN:
                return
         
            # check for delete
            if event.key is pygame.K_BACKSPACE or event.key is pygame.K_DELETE:
                self.text = self.text[:-1]
                return
            
            # ignore special characters
            if event.key in TEXT_BOX_IGNORE:
                return   
         
            # try add the letter
            try:   
                self.text += chr(event.key)
            except ValueError:
                pass
         
      
    #--------------------------------------------------------------------------
      
    def render(self, screen):
        Image.render(self, screen)
      
        text_surf = pygame.font.SysFont("courier", self.fontsize, True).\
                                        render(self.text, True, self.fg_color)
                           
        # where to draw the text
        text_rect = self.rect.inflate(-1 * self.border_width, -1 * self.border_width)
        text_rect.width = text_surf.get_width()
                             
        # offset x slightly so text doesn't touch the border
        text_rect.move_ip(4, 0)
                                 
        screen.blit(text_surf, text_rect)
      
        # create the cursor
        cursor_height = self.rect.height - (self.border_width * 2) - 4
        cursor_surf = pygame.Surface((self._CURSOR_WIDTH, cursor_height))
        cursor_surf.fill(self.fg_color)
      
        cursor_x = text_rect.right + self._CURSOR_WIDTH
        cursor_y = text_rect.top + 2
        cursor_rect = pygame.Rect(cursor_x, cursor_y,
                                self._CURSOR_WIDTH, cursor_height)
      
        # check if the flash timer has elapsed and draw cursor if so
        if self._cursor_toggle and self.has_focus:                          
            screen.blit(cursor_surf, cursor_rect)
      
        # update the cursor flash timer and toggle   
        if self._cursor_flash_time <= 0:
            self._cursor_toggle = not self._cursor_toggle
            self._cursor_flash_time = self._FRAMES_BETWEEN_FLASHES
        else:
            self._cursor_flash_time -= 1
                                  
    #--------------------------------------------------------------------------
      
    def _create_box(self, width, fg_color, bg_color, fontsize, border_width):
        """
        Returns a surface that can be used as the 'box'
        """
      
        # calculate the height based on fontsize
        test_text = pygame.font.SysFont("courier", fontsize, True).\
                                          render("AyQ!", True, (0, 0, 0))
        height = test_text.get_height() + (border_width * 2)
      
        box_surf = pygame.Surface((width, height))
      
        # fill in the foreground colour
        box_surf.fill(fg_color)      
      
        # paint the background colour on top to create hollow rect
        bg_rect = pygame.Rect(border_width, border_width,
                              width - border_width * 2, height - border_width * 2)
        box_surf.fill(bg_color, bg_rect)
      
        return box_surf
      
            
            
         
