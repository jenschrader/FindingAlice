
# *************************************
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 18:41:55 2022
@author: JenSc
"""
# =============================================================================
#  *--Finding Alice--*
# proof of concept for SDEV 148 featuring one lvl
# =============================================================================


# =============================================================================
# # * -- game set up --*
# *************************************
# import stuff
# add sound later..
import pickle
from os import path
import pygame
from pygame.locals import *


# initalize pygame
pygame.init()
clock = pygame.time.Clock()
FPS = 50
# set screen size
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
# create screen display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# set caption
pygame.display.set_caption("Finding Alice")
# define font 
font = pygame.font.Font("PressStart2P-Regular.ttf", 20)
# *************************************
#                                     
# *-- define game variables--*        
# *************************************
TILE_SIZE = 40                        
TILE_SET = 15
GAME_OVER= 0
MAIN_MENU = True
LEVEL = 1
MAX_LEVELS = 2
SOUL_SCORE = 0
GAME_OVER_SCREEN = False
FADE_COUNTER = 0
CUT_SCENE = True
INSTRUCTIONS = False
NEW_BG = False
# *************************************


# *-- define color vars --*
# *************************************
black = (0, 0, 0)
white = (255, 255, 255)
blue = (95, 205, 208)
# *************************************

# *-- load images --*
# *************************************
background = pygame.image.load("assets/bkg.png")
restart_bttn = pygame.image.load("assets/restart.png")
restart_bttn = pygame.transform.scale(restart_bttn, (120, 70))
bg2 = pygame.image.load("assets/lvl2bg.png")
start_bttn = pygame.image.load("assets/start.png")
start_bttn = pygame.transform.scale(start_bttn, (110,70))
exit_bttn = pygame.image.load("assets/exit.png")
exit_bttn = pygame.transform.scale(exit_bttn, (110,70))
door = pygame.image.load("assets/door.png")
you_lose = pygame.image.load("assets/game_over.png")
soul = pygame.image.load("assets/soul.png")
# *************************************
# =============================================================================

# =============================================================================
# *-- methods && classes --*
# *************************************

# *************************************
# display txt method
def create_txt(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x ,y))

# *************************************

# *************************************
# txt method to ensure sentence doesnt exceed screen w/h
def long_txt(text, font, text_col, pos):
    words = [word.split(" ") for word in text.splitlines()]
    space = font.size(" ")[0]
    x, y = pos
    max_width, max_height = screen.get_size()
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, white)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]
                y += word_height
            screen.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height

# *************************************

# *************************************
# method for lvl reset
def reset_lvl(LEVEL):
    player.reset(100, SCREEN_HEIGHT - 160)
    enemy_group.empty()
    gate_group.empty()
    soul_group.empty()
    # load next lvl data
    if path.exists(f"lvl{LEVEL}_data"):
        pickle_open = open(f"lvl{LEVEL}_data", "rb")
        scene_data = pickle.load(pickle_open)
        scene = Scene(scene_data)

    return scene

# *************************************

# *************************************
# grid method
def create_grid():
    for line in range(0, 15):
        pygame.draw.line(screen, (255, 255, 255), (0, line * TILE_SIZE), (SCREEN_WIDTH, line * TILE_SIZE))
        pygame.draw.line(screen, (255, 255, 255), (line * TILE_SIZE, 0), (line * TILE_SIZE, SCREEN_HEIGHT))

# *************************************

# *************************************
# class for button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.click = False

    def draw(self):
        click_action = False

        # mouse pos
        pos = pygame.mouse.get_pos()

        # check if mouse on bttn & if left mouse bttn clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.click is False:
                self.click = True
                click_action = True
        # if left mouse bttn not clicked/ is released, reset the bool
        if pygame.mouse.get_pressed()[0] == 0:
            self.click = False

        # display button
        screen.blit(self.image, self.rect)
        return click_action

# *************************************

# *************************************
# class for player
class Player():
    def __init__(self, x, y):
       # call reset func
        self.reset(x, y)

    # update method
    def update(self, game_over):
        # declaring delta x and y variables
        # and assigning cool down for anims
        delta_x = 0
        delta_y = 0
        walk_cooldown = 6
       # jump_cooldown = 5


        # controls
        # if character isn't dead, do all this stuff
        if GAME_OVER == 0:
            keypress = pygame.key.get_pressed()

            # if left arrow key pressed change x pos -5 px and change dir to left
            if keypress[pygame.K_LEFT]:
                delta_x -= 5
                self.count += 1
                self.direct = -1

            # if right arrow key pressed change x pos +5 px and change dir to right
            if keypress[pygame.K_RIGHT]:
                delta_x += 5
                self.count += 1
                self.direct = 1

            # if left key and right key false reset img count and img index
            # keep character flipped in direction when stopped
            if keypress[pygame.K_LEFT] is False and keypress[pygame.K_RIGHT] is False:
                self.count = 0
                self.index = 0
                if self.direct == 1:
                    self.image = self.anims_right[self.index]
                if self.direct == -1:
                    self.image = self.anims_left[self.index]

            # if space bar pressed change y velocity -15 px
            if keypress[pygame.K_SPACE] and self.jumped is False and self.airborne is False:
                self.vel_y = -13
                self.jumped = True

            if keypress[pygame.K_SPACE] and self.jump_direct == 1:
                self.jump_count += 1
                self.jump_direct = 1

            if keypress[pygame.K_SPACE] and self.jump_direct == -1:
                self.jump_direct = -1


            # if space bar not pressed reset jump variables
            if keypress[pygame.K_SPACE] is False:
                self.jumped = False
                self.jump_count = 0
                self.jump_index = 0
                self.airborne = False
                 # keep dir when stopped
                if self.jump_direct == 1:
                    self.image = self.jump_image
                if self.jump_direct == -1:
                    self.image = self.jump_image

            # anims
            # if img iteration above cooldown time
            if self.count > walk_cooldown:
                # STOP THE COUNT!!!
                self.count = 0
                # increase the list index
                self.index += 1
                # but stop increasing if it goes past the list or equal to end
                if self.index >= len(self.anims_right):
                    # reset the list index, start over anim
                    self.index = 0
                # directions
                if self.direct == 1:
                    self.image = self.anims_right[self.index]
                if self.direct == -1:
                    self.image = self.anims_left[self.index]


            # same thing from above but for jump anims
           # if self.jump_count > jump_cooldown:
            #    self.jump_count = 0
             #   self.jump_index += 1
              #  if self.jump_index >= len(self.anims_rjump):
               #     self.jump_index = 0

               # if self.jump_direct == 1:
                #    self.image = self.anims_rjump[self.jump_index]
               # if self.jump_direct == -1:
                #    self.image = self.anims_ljump[self.jump_index]

            if self.jumped is True:
                if self.direct == 1:
                    self.image = self.jump_image
                if self.direct == -1:
                    self.image = pygame.transform.flip(self.jump_image, True, False )
            # gravity
            self.vel_y += 1
            # jump speed
            self.vel_y = min(self.vel_y, 5)
            #if self.vel_y > 5:
             #   self.vel_y = 5
            delta_y += self.vel_y

            # y pos constantly increase -15 px
            delta_y += self.vel_y

            # collision
            self.airborne = True
            for tile in scene.tile_list:
                # x collision - ensure character can't walk thru walls
                if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.width, self.height):
                    delta_x = 0
                # y collision
                if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):
                    # if jumping - ensure character can't jump thru platforms
                    if self.vel_y < 0:
                        delta_y = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # if falling - ensure character can't fall thru platforms
                    elif self.vel_y >= 0:
                        delta_y = tile[1].top - self.rect.bottom
                        self.airborne = False

            # enemy collision, if collide, character loses
            #enemy_group.add(enemy)
            if pygame.sprite.spritecollide(self, enemy_group, False):
                game_over = -1


            # door collision
            #gate_group.add(gate)
            if pygame.sprite.spritecollide(self, gate_group, False) and SOUL_SCORE > 0:
                game_over = 1

            # update character pos
            self.rect.x += delta_x
            self.rect.y += delta_y

            # if bottom of character rect greater than screen height
           # if self.rect.bottom > SCREEN_HEIGHT:
                # bottom of character rect equals SCREEN_HEIGHT

             #   self.rect.bottom = SCREEN_HEIGHT
              #  delta_y = 0
              
        # if character is dead, show dead img/flip based on dir
        elif GAME_OVER== -1:
            if self.direct == 1:
                self.image = self.dead_image
            if self.direct == -1:
                self.image = pygame.transform.flip(self.dead_image, True, False)


        # display character
        screen.blit(self.image, self.rect)
        # draw rect around character when settin stuff up
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    # reset player method
    def reset(self, x, y):
        # variables and lists
        self.anims_right = []
        self.anims_left = []
        self.anims_rjump = []
        self.anims_ljump = []
        self.index = 0
        self.count = 0
        self.jump_count = 0
        self.jump_index = 0
        # for img num in range of imgs list
        for num in range (1, 5):
            # iterate thru imgs list and assign to right anim variable
            anim_right = pygame.image.load(f"assets/character_sprite{num}.png")
            # scale img
            anim_right = pygame.transform.scale(anim_right, (50, 60))
            # flip img and assign to left anim variable
            anim_left = pygame.transform.flip(anim_right, True, False)
            # add to lists
            self.anims_right.append(anim_right)
            self.anims_left.append(anim_left)
        # same as above but with jump anims
        for num in range(6, 9):
            anim_rjump = pygame.image.load(f"assets/character_sprite{num}.png")
            anim_rjump = pygame.transform.scale(anim_rjump, (50, 60))
            anim_ljump = pygame.transform.flip(anim_rjump, True, False)
            self.anims_rjump.append(anim_rjump)
            self.anims_ljump.append(anim_ljump)

        # variables
        dead_image = pygame.image.load("assets/character_game_over.png")
        dead_image = pygame.transform.scale(dead_image, (50, 60))
        jump_image = pygame.image.load("assets/character_sprite9.png")
        jump_image = pygame.transform.scale(jump_image, (50, 60))
        self.jump_image = jump_image
        self.dead_image = dead_image
        self.image = self.anims_right[self.index]
        self.image = self.anims_rjump[self.jump_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direct = 0
        self.jump_direct = 0
        self.jump = 0
        self.airborne = False

# *************************************

# *************************************
# class for game scene layout
class Scene():
    def __init__(self, data):
        self.tile_list = []
        # load and assign imgs to tile for list
       # tile_3 = pygame.image.load("tile3.png")
       # tile_10 = pygame.image.load("tile10.png")
       # tile_2 = pygame.image.load("tile2.png")
       # tile_6 = pygame.image.load("tile6.png")
       # tile_5 = pygame.image.load("tile5.png")
       # tile_7 = pygame.image.load("tile7.png")
       # tile_4 = pygame.image.load("tile4.png")
       # tile_1 = pygame.image.load("tile1.png")
       # tile_9 = pygame.image.load("tile9.png")
       # tile_11 = pygame.image.load("tile11.png")
       # tile_12 = pygame.image.load("tile12.png")
        #tile_15 = pygame.image.load("tile15.png")
        #tile_16 = pygame.image.load("tile16.png")

        brick = pygame.image.load("assets/brick.png")
        ceiling = pygame.image.load("assets/ceiling.png")
        ground = pygame.image.load("assets/ground.png")
        l_side = pygame.image.load("assets/l_side.png")
        r_side = pygame.image.load("assets/r_side.png")
        l_top_corner = pygame.image.load("assets/l_top_corner.png")
        r_top_corner = pygame.image.load("assets/r_top_corner.png")
        l_bot_corner = pygame.image.load("assets/l_bot_corner.png")
        r_bot_corner = pygame.image.load("assets/r_bot_corner.png")
        #door = pygame.image.load("door.png")
        filler = pygame.image.load("assets/filler.png")
        evil_character = pygame.image.load("assets/evil_character1.png")
        evil_character = pygame.transform.scale(evil_character, (50,60))

        # sets up what tiles go where in rows and columns
        # corresponds with lvl editor data
        row_count = 0
        for row in data:
            column_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(ground,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 2:
                    img = pygame.transform.scale(ceiling,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 3:
                    img = pygame.transform.scale(l_side,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 4:
                    img = pygame.transform.scale(r_side,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 5:
                    img = pygame.transform.scale(l_bot_corner,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 6:
                    img = pygame.transform.scale(r_bot_corner,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 7:
                    img = pygame.transform.scale(r_top_corner,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 8:
                    img = pygame.transform.scale(l_top_corner,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 9:
                    img = pygame.transform.scale(brick,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 10:
                    gate = Gate(column_count * TILE_SIZE, row_count * TILE_SIZE - (TILE_SIZE // 2))
                    gate_group.add(gate)


                if tile == 11:
                    enemy = MainEnemy(column_count * TILE_SIZE, row_count * TILE_SIZE + 15)
                    enemy_group.add(enemy)

                if tile == 12:
                    img = pygame.transform.scale(filler,(TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = column_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)


                if tile == 13:
                    soul = Soul(column_count * TILE_SIZE + (TILE_SIZE // 2), row_count * TILE_SIZE + (TILE_SIZE // 2))
                    soul_group.add(soul)


                            #img = pygame.transform.scale(tile_15,(50, 80))
                            #img_rect = img.get_rect()
                            #img_rect.x = column_count * TILE_SIZE
                            #img_rect.y = row_count * TILE_SIZE
                            #tile = (img, img_rect)
                            #self.tile_list.append(tile)
                column_count += 1
            row_count += 1

    # display method for tiles
    def display(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # uncomment when you want to see grid lines for tiles
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# *************************************

# *************************************
# enemy class that takes sprite args
class MainEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        evil_character = pygame.image.load("assets/evil_character1.png")
        evil_character = pygame.transform.scale(evil_character, (50,60))

       # self.enemy_anims_r = []
       # self.enemy_anims_l = []
       # self.index = 0
       # self.count = 0
       # for num in range (1, 3):
        #    enemy_anim_r = pygame.image.load(f"evil_character{num}.png")
            #enemy_anim_r = pygame.image.load("tile13.png")
         #   enemy_anim_r = pygame.transform.scale(enemy_anim_r, (50, 60))
          #  enemy_anim_l = pygame.transform.flip(enemy_anim_r, True, False)
           # self.enemy_anims_r.append(enemy_anim_r)
           # self.enemy_anims_l.append(enemy_anim_l)

        self.image = evil_character
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move = 1
        self.move_count = 0
        self.move_dir = 1

    def update(self):
       # enemy_cooldown = 5
        self.rect.x += self.move
        self.move_count += 1

        # make the enemy move back and forth every 50 px if greater than cooldown
        #if self.count > enemy_cooldown:
         #   self.count = 0
            #self.index += 1
            #if self.index >= len(self.enemy_anims_r):
             #   self.index = 0

        # enemy turns around every 50 px
        if abs(self.move_count) > 80:
            self.move *= -1
            self.move_count *= -1
            self.move_dir = -1
            if self.move_dir == 1:
                self.image = self.image
            if self.move_dir == -1:
                self.image = pygame.transform.flip(self.image, True, False)
#screen.blit(self.image, self.rect)

# *************************************

# *************************************
class Soul(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/soul.png")
        self.image = pygame.transform.scale(img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# *************************************

# *************************************
class Gate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/door.png")
        self.image = pygame.transform.scale(img, (80, 60))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# *************************************

# *************************************
# class instances
player = Player(100, SCREEN_HEIGHT - 160)

enemy_group = pygame.sprite.Group()
soul_group = pygame.sprite.Group()
gate_group = pygame.sprite.Group()



# img for soul score
score_img = pygame.transform.scale(soul, (TILE_SIZE , TILE_SIZE ))

#soul_group.add(score_img)
#enemy = MainEnemy(90, SCREEN_HEIGHT - 540)

#gate = Gate(100, SCREEN_HEIGHT - 140)

# load in lvl data
if path.exists(f"lvl{LEVEL}_data"):
    # read the data in the corresponding data file (list iteration)
    pickle_open = open(f"lvl{LEVEL}_data", "rb")
    scene_data = pickle.load(pickle_open)
    scene = Scene(scene_data)

# buttons
restart = Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 200, restart_bttn)
start = Button(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 200, start_bttn)
done = Button(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 200, exit_bttn)
# *************************************
# =============================================================================



# =============================================================================
# *-- game loop --*
# *************************************
# game loop control variable
PLAY = True
# start of loop
while PLAY:

    # set frame rate
    clock.tick(FPS)
    # send bg to screen
    screen.blit(background,(0,0))

    # dont start lvl until start button pressed
    # if exit button pressed, quit the program

    if MAIN_MENU is True:

        if CUT_SCENE is True:
            screen.fill(black)
            long_txt("After experiencing a terrible accident,\n"
            "Alice is transported\nto the spirit world\n"
            "where she must collect\nthe pieces of "
            "her\nfractured soul in order\nto return home.\n"
            "\n\n\n\n\n"
            "Veggie must overcome the fear of death, which has\n"
            "manifested in the form of shadow selves, while she adventures "
            "further and further into the unknown... ", font, white,( 30, 50))
            create_txt("*press enter to continue*", font, white, 40, 500)
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                CUT_SCENE = False
                INSTRUCTIONS = True

        if INSTRUCTIONS is True:
            screen.fill(black)
            if done.draw():
                PLAY = False
            if start.draw():
                MAIN_MENU = False
            long_txt("       how to play\n"
                     "       -----------"
                     "\n\n\n\n"
                     "* use left and right arrow\n  keys to move"
                     "\n\n\n\n"
                     "* press space to jump"
                     "\n\n\n\n\n"
                     "* collect soul shards to\n  advance to the next level"
                     "\n\n\n\n"
                     "* watch out for your shadow\n  selves!", font, white, (30, 50))

    else:
        # display lvl scene
        scene.display()
        screen.blit(score_img, (0,0))
        #enemy.update()
        if GAME_OVER== 0:
        # move enemies
            enemy_group.update()
            # check for soul collision and increase score
            if pygame.sprite.spritecollide(player, soul_group, True):
                SOUL_SCORE += 1
            create_txt(" x " + str(SOUL_SCORE), font, white, TILE_SIZE - 10, 10 )


        # display enemies
        enemy_group.draw(screen)
        # display exits
        gate_group.draw(screen)
        # display souls
        soul_group.draw(screen)
        # display character
        GAME_OVER= player.update(GAME_OVER)


        # if player dead do all this
        if GAME_OVER== -1:
            # transition 
            if FADE_COUNTER < SCREEN_WIDTH:
                FADE_COUNTER += 5
                pygame.draw.circle(screen, black, (300,300),  FADE_COUNTER - SCREEN_HEIGHT + SCREEN_WIDTH / 1.5)

            if FADE_COUNTER >= SCREEN_WIDTH:
                GAME_OVER_SCREEN = True
                screen.blit(you_lose, (0, 0))
                if restart.draw():
                    scene_data = []
                    scene = reset_lvl(LEVEL)
                  # reset game control variables
                    GAME_OVER= 0
                    GAME_OVER_SCREEN = False
                    FADE_COUNTER = 0
                    SOUL_SCORE = 0
                if done.draw():
                    PLAY = False
        #create_grid()
        if SOUL_SCORE == 2:
            create_txt("you win!", font, white, 220, 60)
        # if player wins LEVEL
        if GAME_OVER== 1:
            # go to nxt lvl
            LEVEL += 1
            if LEVEL == 2:
                background = bg2
                screen.blit(bg2, (0,0))

            if LEVEL <= MAX_LEVELS:
                # restart LEVEL
                scene_data = []
                scene = reset_lvl(LEVEL)
                GAME_OVER= 0

            else:
                # restart game
                if restart_bttn.draw():
                    LEVEL = 1
                    scene_data = []
                    scene = reset_lvl(LEVEL)
                    GAME_OVER= 0


    # if user clicks X button, end the program
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            PLAY = False

    # update all portions of screen
    pygame.display.update()
# *************************************
# =============================================================================
    # *-- game end --*
pygame.quit()
# =============================================================================
#Footer
#© 2022 GitHub, Inc.
#Footer navigation

    ## Privacy
    ## Security
    ## Status
    ## Docs
    ## Contact GitHub
    ## Pricing
    ## API
    ## Training
    ## Blog
    ## About








if __name__ == "__main__":
    pass  
# *************************************
