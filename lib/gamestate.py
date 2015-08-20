##############################################################################
# gamestate.py
##############################################################################
# Classes related to the game play state.
##############################################################################
# 12/12 Flembobs
##############################################################################
 
import pygame  # @UnusedImport
import random, math
from weakref import WeakKeyDictionary  # @UnusedImport
from graphics.spritesheet import *  # @UnusedWildImport
from engine.model import *  # @UnusedWildImport
from engine.events import *  # @UnusedWildImport
from engine.systemevents import *  # @UnusedWildImport
 
from gui import *  # @UnusedWildImport
 
##############################################################################
# GAME EVENTS
##############################################################################

class SpaceBarEvent(Event):
    """
    Generated when space bar is pressed to raise the pipe.
    """
    def __init__(self):
        pass

class IncrementScoreEvent(Event):
    """
    Generated when pipe passes an obstacle.
    """
    def __init__(self):
        pass

class GameOverEvent(Event):
    """
    Generated when pipe hits an obstacle or the ground.
    """
    def __init__(self):
        pass

class NewGameEvent(Event):
    """
    Generated when player wants to start another game.
    """
    def __init__(self):
        pass

##############################################################################
# GAME EVENTS - MANAGER AND LISTENER CLASSES
##############################################################################
 
class GameEventManager(EventManager):
    listeners = WeakKeyDictionary()
 
class GameEventListener(Listener):
    
    def __init__(self):
        Listener.__init__(self, GameEventManager)
 
##############################################################################
# GAME OBJECTS - MAN
##############################################################################

class Sprite(GameObject, GameEventListener):
    def __init__(self, pos, image):
        GameEventListener.__init__(self)
        self.pos = pos
        self.surf = image
    
    def render(self, screen):
        screen.blit(self.surf, self.pos)
    
    def update(self):
        pass
    
    def notify(self, event):
        pass
    
    def get_rect(self):
        return self.surf.get_rect()
    
    def get_width(self):
        return self.surf.get_width()

class AnimatedSprite(GameObject, GameEventListener):
    def __init__(self, pos, image_list, rate, x_velocity):
        GameEventListener.__init__(self)
        self.pos = list(pos)
        self.surf_list = []
        for image in image_list:
            self.surf_list.append(Sprite(pos, image))
        self.index = 0
        self.tick = 0
        self.rate = rate
        self.x_velocity = x_velocity
        self.can_move = True
    
    def game_over(self):
        self.can_move = False
    
    def get_surf(self):
        return self.surf_list[self.index].surf
    
    def iterate(self):
        self.index += 1
        if self.index >= len(self.surf_list):
            self.index = 0
    
    def render(self, screen):
        screen.blit(self.get_surf(), self.pos)
        self.update()
    
    def update(self):
        if self.tick >= self.rate:
            self.tick = 0
            self.iterate()
        else:
            self.tick += 1
        if self.can_move:
            self.pos[0] -= self.x_velocity
    
    def update_x_pos(self, x_pos):
        self.pos[0] = x_pos
    
    def notify(self, event):
        pass
    
    def get_rect(self):
        rect = self.get_surf().get_rect()
        rect.topleft = self.surf_list[self.index].pos
        return rect
    
    def get_x_velocity(self):
        return self.x_velocity

class Obstacle(GameObject, GameEventListener):
    def __init__(self, x_pos, image_list, rate, number_above, gap_height, total_height, x_velocity):
        GameEventListener.__init__(self)
        self.image_list = image_list
        self.rate = rate
        self.number_above = number_above
        self.gap_height = gap_height
        self.total_height = total_height
        self.obstacle_list = []
        self.obstacle_height = image_list[0].get_height()
        
        # create list of AnimatedSprites (None indicates no obstacle)
        for obstacle in xrange(self.number_above):
            self.obstacle_list.append(AnimatedSprite((x_pos,obstacle*self.obstacle_height),
                                                     image_list,rate,x_velocity))
        for obstacle in xrange(self.gap_height):
            self.obstacle_list.append(None)
        for obstacle in xrange(self.total_height - self.number_above - self.gap_height):
            self.obstacle_list.append(AnimatedSprite((x_pos,(obstacle+self.number_above+self.gap_height)*self.obstacle_height),
                                                     image_list,rate,x_velocity))
    
    def game_over(self):
        for obstacle in self.obstacle_list:
            if obstacle is not None:
                obstacle.game_over()
    
    def update_obstacle(self, number_above, gap_height, tick):
        # get new orientation
        self.number_above = number_above
        self.gap_height = gap_height
        x_pos = self.get_x_pos()
        x_velocity = self.get_obstacle_list_wo_none()[0].get_x_velocity()
        self.obstacle_list = []
        for obstacle in xrange(self.number_above):
            self.obstacle_list.append(AnimatedSprite((x_pos,obstacle*self.obstacle_height),
                                                     self.image_list,self.rate,x_velocity))
        for obstacle in xrange(self.gap_height):
            self.obstacle_list.append(None)
        for obstacle in xrange(self.total_height - self.number_above - self.gap_height):
            self.obstacle_list.append(AnimatedSprite((x_pos,(obstacle+self.number_above+self.gap_height)*self.obstacle_height),
                                                     self.image_list,self.rate,x_velocity))
        
        # synchronize tick
        for obstacle in self.obstacle_list:
            if obstacle is not None:
                obstacle.tick = tick
    
    def get_tick(self):
        return self.get_obstacle_list_wo_none()[0].tick
    
    def get_x_pos(self):
        return self.get_obstacle_list_wo_none()[0].pos[0]
    
    def update_x_pos(self, x_pos):
        for obstacle in self.obstacle_list:
            if obstacle is not None:
                obstacle.update_x_pos(x_pos)
    
    def get_obstacle_height(self):
        return self.obstacle_height
    
    def get_width(self):
        return self.get_obstacle_list_wo_none()[0].get_surf().get_width()
    
    def get_obstacle_list_wo_none(self):
        return [i for i in self.obstacle_list if i is not None]
    
    def get_collision_rects(self):
        collision_rects = []
        if self.number_above > 0:
            collision_rects.append(Rect(self.get_obstacle_list_wo_none()[0].pos,
                                        (self.get_obstacle_list_wo_none()[0].get_rect().width,
                                         self.get_obstacle_list_wo_none()[0].get_rect().height*self.number_above)))
        bottom_obs_index = self.number_above + self.gap_height
        number_below = self.total_height - bottom_obs_index
        if number_below > 0:
            collision_rects.append(Rect(self.obstacle_list[bottom_obs_index].pos,
                                        (self.obstacle_list[bottom_obs_index].get_rect().width,
                                         self.obstacle_list[bottom_obs_index].get_rect().height*number_below)))
        return tuple(collision_rects)
    
    def render(self, screen):
#         for rect in self.get_collision_rects(): # DEBUG: render collision rects
#             pygame.draw.rect(screen, (0,0,0), rect)
        for obstacle in self.obstacle_list:
            if obstacle is not None:
                obstacle.render(screen)
        self.update()
    
    def update(self):
        pass
    
    def notify(self, event):
        pass

class PipePlayer(Sprite):
    def __init__(self, x_pos, image, starting_height, x_velocity, gravity=0.77, max_rise_speed=-9.4, max_fall_speed=18.8, contraction=-20):
        Sprite.__init__(self, (x_pos, starting_height), image)
        self.height = starting_height
        self.gravity = gravity
        self.max_rise_speed = max_rise_speed
        self.max_fall_speed = max_fall_speed
        self.contraction = contraction # number of px that collision rect is contracted
        # negative y-velocity is up, positive y-velocity is down
        
        self.x_pos = x_pos
        self.x_velocity = x_velocity
        self.y_velocity = 0
        self.prev_angle = self.get_ideal_angle()
        self.current_angle = self.get_ideal_angle()
        
        self.game_started = False
    
    def get_ideal_angle(self):
        dampening_factor = 0.2
        return -math.degrees(math.atan(self.y_velocity / float(self.x_velocity))) * dampening_factor
    
    def get_pos(self):
        ARB_DIM = 600
        ceiling_rect = Rect(-1,-ARB_DIM,ARB_DIM,ARB_DIM)
        while ceiling_rect.colliderect(self.get_collision_rect(False)): # prevent pipe from going above ceiling
            self.height += 1
        return (self.x_pos, self.height)
    
    def get_surf(self):
        # figure out angle
        max_change_angle = 5
        self.current_angle = self.get_ideal_angle()
        if self.prev_angle < self.current_angle: # if angle is increasing, pipe is rising
            # limit on how fast the pipe's angle can rise
            self.current_angle = min(self.prev_angle + max_change_angle, self.current_angle)
        self.prev_angle = self.current_angle
        
        return pygame.transform.rotate(self.surf.copy(), self.current_angle)
    
    def get_collision_rect(self, apply_contraction = True):
        height = self.surf.get_height()
        width = self.surf.get_width()
        angle = abs(math.radians(self.current_angle))
        collision_rect = Rect(self.x_pos, self.height,
                              height * math.sin(angle) + width * math.cos(angle),
                              width * math.sin(angle) + height * math.cos(angle))
        if apply_contraction:
            return collision_rect.inflate(self.contraction,self.contraction)
        else:
            return collision_rect
    
    def render(self, screen):
        # pygame.draw.rect(screen, (0,0,0), self.get_collision_rect()) # DEBUG: collision rect
        screen.blit(self.get_surf(), self.get_pos())
        self.update()
    
    def update(self):
        if self.game_started:
            self.y_velocity += self.gravity
            if self.y_velocity >= self.max_fall_speed:
                self.y_velocity = self.max_fall_speed
            self.height += self.y_velocity
    
    def notify(self, event):
        if isinstance(event, SpaceBarEvent):
            self.y_velocity = self.max_rise_speed
            self.game_started = True
            
##############################################################################
# GAME STATE CLASS
##############################################################################

class IntroState(State, SystemEventListener, GUIEventListener):
    def __init__(self, screensize): # TODO: implement sound effects
        State.__init__(self, SystemEventListener, GUIEventListener)
        # logo animation variables
        self.phase = 0
        self.speed = 2*math.pi/90 # radians per frame
        self.amplitude = screensize[1]/50
        self.screensize = screensize
        
        # scrolling animation variables
        self.x_displacement = 0.
        self.x_velocity = 3.575
        
        # construct a list of sprites
        self.spritesheet = Spritesheet(sys.path[0] + SS_NAME)
        self.img_dict = {}
        colorkey = False
        for name in RECT_DICT.keys():
            self.img_dict[name] = pygame.transform.scale2x(self.spritesheet.image_at(RECT_DICT[name], colorkey)) # smooth-scaled 2x
        
        # background
        self.background1 = Image(self.img_dict['background'].get_rect(), self.img_dict['background'])
        self.background1.rect.topleft = (0,0)
        self.game_objects.append(self.background1)
        self.background2 = Image(self.img_dict['background'].get_rect(), pygame.transform.flip(self.img_dict['background'],True,False))
        self.background2.rect.bottomright = screensize
        self.game_objects.append(self.background2)
        
        # terrain (terrain is 308 wide; screen is 576 wide)
        self.terrain1 = Image(self.img_dict['terrain'].get_rect(), self.img_dict['terrain'])
        self.terrain1.rect.bottomleft = (0,screensize[1])
        self.game_objects.append(self.terrain1)
        self.terrain2 = Image(self.img_dict['terrain'].get_rect(), self.img_dict['terrain'])
        self.terrain2.rect.bottomleft = self.terrain1.rect.bottomright
        self.game_objects.append(self.terrain2)
        self.terrain3 = Image(self.img_dict['terrain'].get_rect(), self.img_dict['terrain'])
        self.terrain3.rect.bottomleft = self.terrain2.rect.bottomright
        self.game_objects.append(self.terrain3)
        
        # logos
        self.logo = Image(self.img_dict['logo'].get_rect(), self.img_dict['logo'])
        self.logo.rect.left = screensize[0]/5
        self.logo.rect.centery = screensize[1]/4 # centered
        self.game_objects.append(self.logo)
        self.pipe = Image(self.img_dict['player'].get_rect(), self.img_dict['player'])
        self.pipe.rect.right = 4*screensize[0]/5
        self.pipe.rect.centery = screensize[1]/4 # centered
        self.game_objects.append(self.pipe)
        
        # buttons
        self.button = Button(self.img_dict['start'].get_rect(), self.img_dict['start'])
        self.button.rect.centerx = screensize[0]/2
        self.button.rect.centery = 3*screensize[1]/4
        self.game_objects.append(self.button)
        
        # construct fadescreen (should be last)
        self.fade = FadeScreen(-5,255,screensize)
        self.game_objects.append(self.fade)
    
    def notify(self, event):
        if isinstance(event, TickEvent):
            # logo oscillation
            self.logo.rect.centery = self.screensize[1]/4 + self.amplitude*math.sin(self.phase)
            self.pipe.rect.centery = self.screensize[1]/4 + self.amplitude*math.sin(self.phase)
            
            # scrolling
            self.terrain1.rect.bottomleft = ((self.terrain1.rect.width + self.x_displacement) % -self.terrain1.rect.width,
                                             self.screensize[1])
            self.terrain2.rect.bottomleft = self.terrain1.rect.bottomright
            self.terrain3.rect.bottomleft = self.terrain2.rect.bottomright
            
            SystemEventManager.post(DrawRequestEvent(self.game_objects))
            self.phase += self.speed
            self.x_displacement -= self.x_velocity
        if isinstance(event, ButtonClickedEvent) and self.fade.get_alpha() == 0: # start button starts fade-into game
            self.fade.set_alpha(0)
            self.fade.set_speed(5)
            self.fade.set_end_event(255, FadeIntoGameEvent)
        if isinstance(event, FadeIntoGameEvent):
            self.fade.delete_end_event()
            Model.change_state(GameState(self.fade, self.img_dict, self.screensize))

class GameState(State, SystemEventListener, GUIEventListener): # main game state
    def __init__(self, fade_screen, img_dict, screensize):
        State.__init__(self, SystemEventListener, GUIEventListener)
        
        self.fade = fade_screen
        self.img_dict = img_dict
        self.game_started = False
        
        # scrolling animation variables
        self.x_displacement = 0.
        self.x_velocity = 3.575 # TODO: make self.x_velocity an integer OBJECT to allow for variable speed
        self.screensize = screensize
        
        # obstacle settings
        self.distance_between_pipes = 320.4
        self.total_height = 17
        self.gap_height = 7
        
        # background
        self.background1 = Image(self.img_dict['background'].get_rect(), self.img_dict['background'])
        self.background1.rect.topleft = (0,0)
        self.game_objects.append(self.background1)
        self.background2 = Image(self.img_dict['background'].get_rect(), pygame.transform.flip(self.img_dict['background'],True,False))
        self.background2.rect.bottomright = screensize
        self.game_objects.append(self.background2)
        
        # terrain (terrain is 308 wide; screen is 576 wide)
        self.terrain1 = Image(self.img_dict['terrain'].get_rect(), self.img_dict['terrain'])
        self.terrain1.rect.bottomleft = (0,screensize[1])
        self.game_objects.append(self.terrain1)
        self.terrain2 = Image(self.img_dict['terrain'].get_rect(), self.img_dict['terrain'])
        self.terrain2.rect.bottomleft = self.terrain1.rect.bottomright
        self.game_objects.append(self.terrain2)
        self.terrain3 = Image(self.img_dict['terrain'].get_rect(), self.img_dict['terrain'])
        self.terrain3.rect.bottomleft = self.terrain2.rect.bottomright
        self.game_objects.append(self.terrain3)
        
        # obstacles
        self.obstacle1 = Obstacle(-100, (img_dict['fb1'], img_dict['fb2'], img_dict['fb3'], img_dict['fb2']),
                                  5, self.get_gap(self.total_height,self.gap_height),
                                  self.gap_height, self.total_height, self.x_velocity)
        self.game_objects.append(self.obstacle1)
        self.obstacle2 = Obstacle(-100, (img_dict['fb1'], img_dict['fb2'], img_dict['fb3'], img_dict['fb2']),
                                  5, self.get_gap(self.total_height,self.gap_height),
                                  self.gap_height, self.total_height, self.x_velocity)
        self.game_objects.append(self.obstacle2)
        self.obstacle1_passed, self.obstacle2_passed = True, True
        
        # player
        self.score = 0
        self.player = PipePlayer(screensize[0]/4, img_dict['player'],
                                 (screensize[1] - self.img_dict['terrain'].get_height())/2,
                                 self.x_velocity)
        self.game_objects.append(self.player)
        
        # instructions
        self.instructions = Sprite((screensize[0]/2,(screensize[1] - self.img_dict['terrain'].get_height())/2),
                                   img_dict['instructions'])
        self.game_objects.append(self.instructions)
        
        # score tag
        fontsize = 40
        self.score_tag = Text(str(self.score), (255, 255, 255), fontsize, 'flappybird.ttf', False)
        self.score_tag.rect.centerx = screensize[0]/2
        self.score_tag.rect.centery = screensize[1]/10
        self.game_objects.append(self.score_tag)
        
        # construct fadescreen (should be last)
        self.fade = FadeScreen(-5,255,screensize)
        self.game_objects.append(self.fade)
        
        self.terrain_collision_rect = Rect(self.terrain1.rect.unionall([self.terrain2.rect, self.terrain3.rect])) # terrain collision rect
    
    def notify(self, event):   
        if isinstance(event, TickEvent):
            # scrolling
            self.terrain1.rect.bottomleft = ((self.terrain1.rect.width + self.x_displacement) % -self.terrain1.rect.width,
                                             self.screensize[1])
            self.terrain2.rect.bottomleft = self.terrain1.rect.bottomright
            self.terrain3.rect.bottomleft = self.terrain2.rect.bottomright
            
            # update obstacle positions and orientations
            if self.game_started:
                if self.obstacle1.get_x_pos() <= -self.obstacle1.get_width():
                    self.obstacle1.update_obstacle(self.get_gap(self.total_height, self.gap_height), self.gap_height, self.obstacle2.get_tick())
                    self.obstacle1.update_x_pos(self.obstacle2.get_x_pos() + self.distance_between_pipes)
                    self.obstacle1_passed = False
                if self.obstacle2.get_x_pos() <= -self.obstacle2.get_width():
                    self.obstacle2.update_obstacle(self.get_gap(self.total_height, self.gap_height), self.gap_height, self.obstacle1.get_tick())
                    self.obstacle2.update_x_pos(self.obstacle1.get_x_pos() + self.distance_between_pipes)
                    self.obstacle2_passed = False
            
            # update score
            if not self.obstacle1_passed:
                if self.player.get_pos()[0] + self.player.get_width()/2 >= self.obstacle1.get_x_pos(): # center of player aligns with leftside of obstacle
                    self.obstacle1_passed = True
                    SystemEventManager.post(IncrementScoreEvent())
            if not self.obstacle2_passed:
                if self.player.get_pos()[0] + self.player.get_width()/2 >= self.obstacle2.get_x_pos():
                    self.obstacle2_passed = True
                    SystemEventManager.post(IncrementScoreEvent())
            
            # collision check
            collision_rects = list(self.obstacle1.get_collision_rects()) + list(self.obstacle2.get_collision_rects())
            collision_rects.append(self.terrain_collision_rect)
            if self.player.get_collision_rect().collidelistall(collision_rects) != []:
                SystemEventManager.post(GameOverEvent())
            
            SystemEventManager.post(DrawRequestEvent(self.game_objects))
            self.x_displacement -= self.x_velocity
        
        if isinstance(event, KeyboardEvent):
            if event.key == pygame.K_ESCAPE:
                SystemEventManager.post(QuitEvent())
            if event.key == pygame.K_SPACE and self.fade.get_alpha() == 0: # space bar press
                GameEventManager.post(SpaceBarEvent())
                if not self.game_started: # remove instructions from screen if not already done
                    self.game_objects.remove(self.instructions)
                    self.game_started = True
                    self.obstacle1.update_x_pos(self.distance_between_pipes * 2 - self.x_displacement)
                    self.obstacle2.update_x_pos(self.distance_between_pipes * 3 - self.x_displacement)
                    self.obstacle1_passed, self.obstacle2_passed = False, False
        
        if isinstance(event, IncrementScoreEvent):
            self.score += 1
            self.score_tag.update(str(self.score))
            self.score_tag.rect.centerx = self.screensize[0]/2
            self.score_tag.rect.centery = self.screensize[1]/10
        
        if isinstance(event, GameOverEvent): # when game is over, switch to GameOverState
            Model.change_state(GameOverState((self.background1, self.background2),
                                             (self.terrain1, self.terrain2, self.terrain3),
                                             (self.obstacle1, self.obstacle2), self.player, self.score_tag,
                                             self.fade, self.img_dict, self.screensize, self.score))

    def get_gap(self, total_height, gap_height): # 17 birds tall, gaps are 6 birds tall
        return random.randint(0,total_height-gap_height)

class GameOverState(State, SystemEventListener, GUIEventListener):
    def __init__(self, background_list, terrain_list, obstacle_list, player, score_tag, fade_screen, img_dict, screensize, score):
        State.__init__(self, SystemEventListener, GUIEventListener)
        self.player = player
        self.fade = fade_screen
        self.img_dict = img_dict
        self.screensize = screensize
        self.score = score
        
        for background in background_list:
            self.game_objects.append(background)
        for terrain in terrain_list:
            self.game_objects.append(terrain)
        for obstacle in obstacle_list:
            obstacle.game_over()
            self.game_objects.append(obstacle)
        self.game_objects.append(self.player)
        
        # score tag (will disappear after player falls offscreen)
        self.score_tag = score_tag
        self.game_objects.append(self.score_tag)
        
        # gameover tag (will appear after player falls offscreen)
        self.gameover_tag = Image(self.img_dict['gameover'].get_rect(), self.img_dict['gameover'])
        self.gameover_tag.rect.centerx = self.screensize[0]/2
        self.gameover_tag.rect.centery = -self.screensize[1]
        self.game_objects.append(self.gameover_tag)
        
        # score background tag (will appear after player falls offscreen)
        self.score_bg = Image(self.img_dict['scorebg'].get_rect(), self.img_dict['scorebg'])
        self.score_bg.rect.centerx = self.screensize[0]/2
        self.score_bg.rect.centery = self.screensize[1]*3/2
        self.game_objects.append(self.score_bg)
        
        # scores
        fontsize = 24
        self.final_score_tag = Text(str(self.score), (255,255,255), fontsize, 'flappybird.TTF', False)
        self.final_score_tag.rect.centery = self.screensize[1]*2
        self.game_objects.append(self.final_score_tag)
        # TODO: implement high score
#         self.high_score_tag = None
#         self.game_objects.append(self.high_score_tag)
        
        # restart button
        self.restart_button = Button(self.img_dict['ok'].get_rect(), self.img_dict['ok'])
        self.restart_button.rect.centerx = self.screensize[0]/2
        self.restart_button.rect.centery = self.screensize[1]*2
        self.game_objects.append(self.restart_button)
        
        # construct fadescreen (should be last)
        self.fade = FadeScreen(-15,255,screensize,(255,255,255))
        self.game_objects.append(self.fade)
    
    def notify(self, event):
        if isinstance(event, TickEvent):
            SystemEventManager.post(DrawRequestEvent(self.game_objects))
            try:
                if self.player.get_pos()[1] > self.screensize[1]*2 and self.fade.get_alpha() == 0:
                    del self.player
            except AttributeError: # self.player has been deleted
                self.score_tag.rect.centerx = self.screensize[0]/2
                self.score_tag.rect.centery = -self.screensize[1]
                self.gameover_tag.rect.centery = self.screensize[1]/5
                if self.score_bg.rect.centery > self.screensize[1]/2:
                    self.score_bg.rect.centery -= self.screensize[1]/20
                else:
                    self.final_score_tag.rect.right = 33*self.screensize[0]/50
                    self.final_score_tag.rect.centery = 9*self.screensize[1]/20
                    self.restart_button.rect.centery = 2*self.screensize[1]/3
        
        if isinstance(event, KeyboardEvent): # DEBUG
            if event.key == pygame.K_r:
                SystemEventManager.post(ButtonClickedEvent(self.restart_button))
        
        if isinstance(event, ButtonClickedEvent) and self.fade.get_alpha() == 0:
            if event.button == self.restart_button:
                self.fade.set_color((0,0,0))
                self.fade.set_alpha(0)
                self.fade.set_speed(5)
                self.fade.set_end_event(255, FadeIntoGameEvent)
        
        if isinstance(event, FadeIntoGameEvent):
            self.fade.delete_end_event()
            Model.change_state(GameState(self.fade, self.img_dict, self.screensize))