#!/usr/bin/env python3
'''
NOTICE: THIS GAME ASSUMES A 1080p RESOLUTION as the screen size is fixed at 960 by 960. I have no idea how to scale it in pygame.

HOW TO PLAY
CONTROLS: arrow keys and z and x keys
Arrow keys are used to move around
X - is your interact key, use this while on top of things to do an action:
buy seeds, pick up and drop flowers, plant seeds in grass, water sprouts
Z - is your attack key you can cut down trees, attack lizards and collect water

GROWING PLANTS: plant a sprout in grass and water it before a full day passes (i.e full night and day cycle pass flower tile)
SELLING PLANTS: put plant in middle area where yellow line passes. Yellow line must pass the flower twice to sell. If player 
picks up flower during this time sell line pass count is reduced to 0 and must be pass twice again.

ENEMIES: lizards will decide to eat flower if on top of it or not. If a lizard hits you, you drop water!
SHOP: buy seeds for $50 flowers sell at a base of $150 + random value. if out of seed, money and flowers you get a free seed!


STUFF I WISHED TO ADD:
Really to increase submission and just the chill vibe of the game I wanted to have a limit on the amount of lizards spawned proportional to the amount of
flowers the player has. But just deleting old lizards looked bad. I was going to try and implement A* but it proved to be a little hard to get down in a reasonable 
amount of time (I was going to try and have them walk back to their dens and despawn). Other things to prevent this would be to stop spawning lizards but this proved to make selling flowers more trivial than intended.
Other things like push blocks to block off dens required more time than I had. I decided on a spawn cap but this is less than ideal as it can make selling flowers quite
trivial.

Sound effects/visual feedback. This game lacks feedback and really needs it but just try and imagine trees shaking when hit and error sounds when you're too poor to
buy items.
'''
import pygame, sys, random, math

from os import path
from pygame.locals import *
from globalvars import *
from sprites import *
from gamemap import *
from lines import *
from tiledata import *

#This displays the water fill bar at the top of the screen
def draw_water_amount(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 300
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pygame.Rect(x,y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, WATER_COL, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 3)

#game is handled an object oriented way this will hold the main game loop
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Meadow")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        #Set game to display title screen
        self.game_state = GameState.TITLE
        self.load()

    def load(self):
        folder = path.dirname(__file__)
        bin_folder = path.join(folder, 'bin')
        map_folder = path.join(folder, 'map')
        self.flower_imgs = get_flower_data(bin_folder)
        self.enemy_data = get_enemy_data(bin_folder)
        self.map = MainMap(map_folder, bin_folder)
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.font = pygame.font.match_font('monospace')
        #load all the base files needed
        self.player_img = pygame.image.load(path.join(bin_folder, PLAYER_IMG)).convert_alpha()
        self.player_img_night = pygame.image.load(path.join(bin_folder, PLAYER_IMG_NIGHT)).convert_alpha()
        self.attack_img = pygame.image.load(path.join(bin_folder, ATTACK_IMG)).convert_alpha()
        self.empty_img = pygame.image.load(path.join(bin_folder, EMPTY_IMG)).convert_alpha()

        self.title_screen = pygame.image.load(path.join(bin_folder, TITLE_IMG)).convert_alpha()
        self.info_screen = pygame.image.load(path.join(bin_folder, INFO_IMG)).convert_alpha()

        #check if attack square is overlaping. Used so constant attack returns are avoided
        self.attack_hitting = False

    def initialize(self):
        #this could have been done a more object oriented way, but pygame groups make getting collisions fast and simple
        #Group for the player used to show player on top of everything
        self.player_group = pygame.sprite.Group()
        #all the sprites with exeption to enemies and players
        self.all_sprites = pygame.sprite.Group()
        #all things that the player cannot walk on
        self.blocks = pygame.sprite.Group()
        #all the lizards
        self.enemies = pygame.sprite.Group()
        #all the active attack tiles
        self.attacks = pygame.sprite.Group()
        #all the tiles that change from night to day, by line collision
        self.changing_tiles = pygame.sprite.Group()
        #all the tiles that are plantable
        self.plantable_tiles = pygame.sprite.Group()
        #all the sprouts on the map
        self.sprouts = pygame.sprite.Group()
        #all the flowers on the map
        self.flowers = pygame.sprite.Group()
        #all the held items
        self.holding = pygame.sprite.Group()
        #all the items the player can buy
        self.shopable = pygame.sprite.Group()
        #all enemies are not enemies
        self.non_enemy = pygame.sprite.Group()

        #get all map tile locations ready to spawn
        self.map.initialize(self)

        #all day lines 
        self.lines = [RotatingLine( (WIDTH/2, HEIGHT/2), 270, [(0.035,0.25), (0.25,1)], DAY_SPEED, False)]
        #sell line 
        self.sell_line = RotatingLine( (WIDTH/2, HEIGHT/2), 90, [(0.04,SELL_LENGTH), (SELL_LENGTH,SELL_LENGTH)], SELL_SPEED, colour=YELLOW, thicc=2)
        #make player with location
        self.player = Player(self, Vector2(5,5))
    
    def execute(self):
        #main loop looks at state displays/updates accordingly
        while True:
            if self.game_state == GameState.TITLE:
                self.game_start_screen(self.screen)

            if self.game_state == GameState.INFO:
                self.player_info_screen(self.screen)

            if self.game_state == GameState.PLAYING:
                self.play_game()
        
            if self.game_state == GameState.QUIT:
                self.clean()
                return
    
    #title screen simply blit the title screen and check if player pressed enter
    def game_start_screen(self, screen):
        #pass in next screen
        self.handle_in_menu(GameState.INFO)
        self.screen.blit(self.title_screen,(0,0))
        pygame.display.flip()
    
    #info screen simply blit the title screen and check if player pressed enter
    def player_info_screen(self, screen):
        #pass in next screen
        self.handle_in_menu(GameState.PLAYING)
        self.screen.blit(self.info_screen,(0,0))
        pygame.display.flip()
    
    #main game loop with delta time
    def play_game(self):
        self.delta = self.clock.tick(FPS) / 1000
        self.handle_in()
        self.update()
        self.render()

    #runs to quit the game
    def clean(self):
        pygame.quit()
        sys.exit()
    
    #handle game playing info. just looking if player is quiting the game. Rest of the input is handled in the player class
    def handle_in(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = GameState.QUIT
    
    #handle menu input. look for return key and switched to passed in next state
    def handle_in_menu(self, next_state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = GameState.QUIT
                if event.key == pygame.K_RETURN:
                    self.game_state = next_state
    
    #UPDATE LOOP
    def update(self):
        #update all sprites
        self.all_sprites.update()
        #update all players 
        self.player_group.update()
        #update all enemies
        self.enemies.update()
        line_did_reset = False

        #rotate day/night line
        for line in self.lines:
            line_did_reset = line.rotate(line.speed)
        
        #rotate sell line
        self.sell_line.rotate(self.sell_line.speed)

        #check if day/night line collides with changeable tiles
        for tile in self.changing_tiles:
            hit = self.update_line_collisions(tile)
            if hit:
                tile.line_hit()
            else:
                tile.line_unhit()
        
        #check if sell line collides with flowers!
        for flower in self.flowers:
            hit = self.update_sell_line_col(flower)
            if hit:
                flower.sell_hit()
            else:
                flower.sell_unhit()

        #check if player collides with lizards!
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for hit in hits:
            self.player.hit(hit)
        
        #check if any enemy is hit by an attack this includes water, lizards and trees
        hits = pygame.sprite.groupcollide(self.enemies, self.attacks, False, False)
        if len(hits) == 0:
            #we not hitting anything anymore
            self.attack_hitting = False
        #dont contantly run function so check if already hit
        elif not self.attack_hitting:
            for hit in hits:
                hit.hit(self.player)
                self.attack_hitting = True

    def render(self):
        #blit the rendered map
        self.screen.blit(self.map_img, (0,0))
        #draw all other sprites
        self.all_sprites.draw(self.screen)
        self.player_group.draw(self.screen)
        self.enemies.draw(self.screen)
        self.holding.draw(self.screen)
        #render sell and day/night lines
        for line in self.lines:
            line.render(self.screen)
        self.sell_line.render(self.screen)
        #RENDER HUD
        draw_water_amount(self.screen, 5, 2, self.player.water_amount / MAX_WATER_AMOUNT)
        self.draw_text('Seeds: ' + str(self.player.seed_amount), self.font, 16, FIELD, 550, 2)
        self.draw_text('Money: ' + str(self.player.money_amount), self.font, 16, YELLOW, 750, 2)
        pygame.display.flip()

    #runs pygame neccesary lines to render text in pygame
    def draw_text(self, text, font_name, size, colour, x, y):
        font = pygame.font.Font(font_name, size)
        txt_surface = font.render(text, True, colour)
        txt_rect = txt_surface.get_rect()
        txt_rect.topleft = (x,y)
        self.screen.blit(txt_surface, txt_rect)

    #update the sell line collisions
    def update_sell_line_col(self, sprite):
        colliding = False
        for segment in self.sell_line.segments:
            if self.detect_collision_line(segment, sprite):
                colliding = True
                break
        return colliding

    #update the day/night line collisions
    def update_line_collisions(self, sprite):
        # Look at every line and see if the input circle collides with any of them; return if collided
        # Assume we aren't colliding
        colliding = False

        # We'll need to look at each of our lines, if we had more than one
        # If any of them are colliding, we can break out because we only need one
        for line in self.lines:
            # Look at each segment of the line
            for segment in line.segments:
                if self.detect_collision_line(segment, sprite):
                    colliding = True
                    break
        return colliding

    def detect_collision_line(self, line_points, sprite):
        # line_points is a pair of points, where each point is a tuple of (x, y) coordinates.
        # Eg. line_points = ( (0, 0), (100, 100) ) represents a line down and right.
        # circle is just a circle class
    
        # unpack u; a line is an ordered pair of points and a point is an ordered pair of co-ordinates
        (u_sol, u_eol) = line_points
        (u_sol_x, u_sol_y) = u_sol
        (u_eol_x, u_eol_y) = u_eol

        # unpack v; a circle is a center point and a radius (and a point is still an ordered pair of co-ordinates)
        (v_ctr, v_rad) = ((sprite.rect.centerx, sprite.rect.centery), TILESIZE -2)
        (v_ctr_x, v_ctr_y) = v_ctr
        # the equation for all points on the line segment u can be considered u = u_sol + t * (u_eol - u_sol), for t in [0, 1]
        # the center of the circle and the nearest point on the line segment (that which we are trying to find) define a line 
        # that is is perpendicular to the line segment u (i.e., the dot product will be 0); in other words, it suffices to take
        # the equation v_ctr - (u_sol + t * (u_eol - u_sol)) · (u_evol - u_sol) and solve for t
        if ((u_eol_x - u_sol_x) ** 2 + (u_eol_y - u_sol_y) ** 2) == 0: return

        t = ((v_ctr_x - u_sol_x) * (u_eol_x - u_sol_x) + (v_ctr_y - u_sol_y) * (u_eol_y - u_sol_y)) / ((u_eol_x - u_sol_x) ** 2 + (u_eol_y - u_sol_y) ** 2)

        # this t can be used to find the nearest point w on the infinite line between u_sol and u_sol, but the line is not 
        # infinite so it is necessary to restrict t to a value in [0, 1]
        t = max(min(t, 1), 0)
    
        # so the nearest point on the line segment, w, is defined as
        w_x = u_sol_x + t * (u_eol_x - u_sol_x)
        w_y = u_sol_y + t * (u_eol_y - u_sol_y)
    
        # Euclidean distance squared between w and v_ctr
        d_sqr = (w_x - v_ctr_x) ** 2 + (w_y - v_ctr_y) ** 2
        
        # if the Eucliean distance squared is less than the radius squared
        if (d_sqr <= v_rad ** 2):
            #sprite.pos_bump(dir_of_cols(Vector2(w_x,w_y), Vector2(v_ctr_x,v_ctr_y)),mag=2,force=True)
            # the line collides
            return True  # the point of collision is (int(w_x), int(w_y))
        
        else:    
            # the line does not collide
            return False


#main game running
def main():
    game = Game()
    while True:
        game.initialize()
        game.execute()
if __name__ == "__main__":
    main()
