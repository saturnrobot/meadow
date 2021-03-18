'''
This is all the sprites in the game and their logic.
'''
import pygame, random
from pygame.locals import *
from globalvars import *

#moveable class all functions relating to movement
class Moveable(pygame.sprite.Sprite):
    def __init__(self, game, loc : Vector2):
        self.game = game
        self.location = Vector2(loc.x,loc.y)
        self.destination = Vector2(loc.x,loc.y)
        self.lastGoodLocation = Vector2(loc.x, loc.y)
        self.rotation = 0

    def move(self, movex=0, movey=0, ignorecols=False):  
        isnotgood = False
        #check if this movement is forced if not check if a valid move
        if not ignorecols: isnotgood = self.check_blocks(movex, movey)
        if not isnotgood:
            self.destination.x += movex
            self.destination.y += movey
    
    #check every frame. looking if sprite has somehow reached invalid area
    def fix_check(self):
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.location = self.lastGoodLocation
            return
        if self.location.x >= WIDTH or self.location.x <= 0 or self.location.y >= HEIGHT or self.location.y <= 0:
            self.location = self.lastGoodLocation
            return
        self.lastGoodLocation = Vector2(self.location.x, self.location.y)

    #check if desired location has a wall. rounded location just incase object smooths its movement
    def check_blocks(self, x, y):
        for block in self.game.blocks:
            if block.location.x == round(self.location.x) + x and block.location.y == round(self.location.y) + y:
                return True
        return False
    
    #bump moveable back by x amount of tiles
    def pos_bump(self, dirh, mag=1, force=False):
        #check for wall based on hit path and reduce it if it exists
        for i in range(mag):
            if self.check_blocks(dirh[0]*mag, dirh[1]*mag):
                mag -= 1
                continue
            break
        self.move(movex=dirh[0]*mag, movey=dirh[1]*mag, ignorecols=force)
    
    #get proper tile based location of sprite
    def get_location(self):
        return Vector2(round(self.location.x) * TILESIZE + TILESIZE/2, round(self.location.y) * TILESIZE + TILESIZE/2)

#this object changes from a day to night tile
class DayHits:
    def __init__(self):
        self.colliding = False
    
    #dont repeat this function wait until new collision
    def line_hit(self):
        if self.colliding: return
        self.colliding = True
    
    def line_unhit(self): self.colliding = False

#this object collides with sell line
class SellHits:
    def __init__(self):
        self.sell_colliding = False
    
    def sell_hit(self):
        if self.sell_colliding: return
        self.sell_colliding = True
    
    def sell_unhit(self):
        self.sell_colliding = False

#this object changes image based on if day/night line hits it. Takes tiles from tiledata.py in data field
class Changeable(DayHits):
    def __init__(self, data, night=False):
        #is night or not
        self.night = night
        #set up day and night tile images
        self.change_day_night_image(data.daytile, data.nighttile)
        super().__init__()

    
    def change_day_night_image(self, day_tile, night_tile):
        self.day_image = day_tile
        self.night_image = night_tile

        if self.night:
            self.image = self.night_image
        else:
            self.image = self.day_image

    def line_hit(self):
        if self.colliding: return

        if self.night:
            self.image = self.day_image
            self.night = False
        else:
            self.image = self.night_image
            self.night = True
        
        self.colliding = True
    
    def get_img(self): return self.image

#this line changes its image based on tile below it's state. this is best for moving objects
class TileCheckChangeable:
    def __init__(self, data, night=False):
        self.night = night
        self.change_day_night_image(data.daytile, data.nighttile)

    def change_day_night_image(self, day_tile, night_tile):
        self.day_image = day_tile
        self.night_image = night_tile

        if self.night:
            self.image = self.night_image
        else:
            self.image = self.day_image
    
    #check if tile below it at location is day or night
    def check_night(self, x, y, stall=False):
        if stall: return
        if x > 0 and y > 0 and x < WIDTH/TILESIZE and y < HEIGHT/TILESIZE:
            self.night = not self.game.map.tiles[(x, y)][0].night
        if self.night:
            self.image = self.day_image
            self.night = False
        else:
            self.image = self.night_image
            self.night = True
    
    def get_img(self): return self.image

#player image data
class PlayerImage:
    def __init__(self, day_img, night_image):
        self.daytile = day_img
        self.nighttile = night_image

#player class is moveable and changes based on tile it is on
class Player(Moveable, TileCheckChangeable):
    #player need game to get from and location to spawn at
    def __init__(self, game, loc):
        TileCheckChangeable.__init__(self,PlayerImage(game.player_img, game.player_img_night))
        super().__init__(game,loc)
        #player is only in player group
        self.groups = game.player_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.rect = self.image.get_rect()
        #put player sprite at location
        self.rect.center = (loc.x, loc.y)
        #set player desired location to they one they on
        self.destination = Vector2(loc.x, loc.y)
        #used for time delays
        self.last = pygame.time.get_ticks()
        self.delay = 0
        #last time attacked
        self.last_attack = 0
        #where are we looking
        self.facing = Vector2(0,-1)
        self.colliding = False
        #changeable amounts/currency
        self.water_amount = 0
        self.money_amount = STARTING_CASH
        self.seed_amount = 0
        #holding based values
        self.interact_holding = False
        self.holding_item = False

    #movement is altered because player may be holding item. If holding item check the blocks arounf the holding item too
    def move(self, movex=0, movey=0, ignorecols=False):  
        isnotgood = False
        if not ignorecols: 
            if self.holding_item:
                flower_vector = Vector2(movex, movey) + self.facing
                isnotgood = self.check_blocks(movex, movey) or self.check_blocks(flower_vector.x, flower_vector.y)
            else:
                isnotgood = self.check_blocks(movex, movey) 
        if not isnotgood:
            self.destination.x += movex
            self.destination.y += movey
    
    #this move handles rotation then moves used mostly for input based movement
    def propermove(self, movex=0, movey=0):
        self.facing = Vector2(movex, movey)
        target_rot = Vector2(movex,movey).angle_to(Vector2(0,-1))% 360
        if target_rot == self.rotation:
            self.move(movex=movex, movey=movey)
            return
        self.rotation = target_rot % 360
        self.set_delay(50)
    
    #when interact key is pressed 
    def interact(self):
        #save current sprout and flower on location player is on
        sprout = self.check_sprouts(0,0)
        flower = self.check_flowers(0,0)
        #if on buyable tile
        if (self.check_buyable(0,0)):
            if (self.money_amount >= SEED_PRICE):
                self.seed_amount += AMOUNT_OF_SEED
                self.money_amount -= SEED_PRICE
            elif (self.seed_amount <= 0 and len(self.game.flowers) <= 0 and len(self.game.sprouts) <= 0):
                self.seed_amount += AMOUNT_OF_SEED
        #if on sprout tile
        elif (sprout):
            if (self.water_amount >= WATER_AMOUNT):
                sprout.water()
                self.water_amount -= WATER_AMOUNT
        #if holding item
        elif (self.holding_item):
            flower_check = self.check_flowers(self.facing.x,self.facing.y)
            #if flower is not being dropped on other flower or wall or sprout
            if(not self.check_sprouts(self.facing.x,self.facing.y) and not flower_check and not self.check_blocks(self.facing.x,self.facing.y)):
                self.holding_item.drop()
                self.holding_item = False
        #if on flower hold it
        elif (flower):
            self.holding_item = flower
            self.holding_item.hold(self)
        #if on plantable tile 
        elif(not flower and not sprout and self.check_plantable(0,0)):
            #if have seed (put this incase wanted to add a shake or feedback)
            if self.seed_amount > 0:
                self.seed_amount -= 1
                pick = random.randint(0,len(self.game.flower_imgs)-1)
                Flower(self.game, self.game.flower_imgs[pick], self.destination.x, self.destination.y, self.night)
        
    #check if player is in valid location
    def fix_check(self):
        if self.location.x > WIDTH or self.location.x < 0 or self.location.y > HEIGHT or self.location.y < 0:
            self.pos_bump(dir_of_cols(Vector2(self.rect.centerx, self.rect.centery), Vector2(WIDTH/2, HEIGHT/2)), 
            3, True)
            return
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.pos_bump(dir_of_cols(Vector2(self.rect.centerx, self.rect.centery), Vector2(WIDTH/2, HEIGHT/2)),1,True)
            return
        self.lastGoodLocation = Vector2(self.destination.x, self.destination.y)

    #check if flower exists at location
    def check_flowers(self, x, y):
        for flower in self.game.flowers:
            if flower.location.x == round(self.location.x) + x and flower.location.y == round(self.location.y) + y:
                return flower
        return False
    
    #check if sprout exists at location
    def check_sprouts(self, x ,y):
        for sprout in self.game.sprouts:
            if sprout.location.x == round(self.location.x) + x and sprout.location.y == round(self.location.y) + y:
                return sprout
        return False
    
    #check if plant exists at location
    def check_plantable(self, x, y):
        for tile in self.game.plantable_tiles:
            if tile.location.x == round(self.location.x) + x and tile.location.y == round(self.location.y) + y:
                return True
        return False
    
    #check if buyable item exists at location
    def check_buyable(self, x, y):
        for tile in self.game.shopable:
            if tile.location.x == round(self.location.x) + x and tile.location.y == round(self.location.y) + y:
                return True
        return False

    #check if wall exist at location
    def check_blocks(self, x, y):
        for block in self.game.blocks:
            if block.location.x == round(self.location.x) + x and block.location.y == round(self.location.y) + y:
                return True
        return False

    #get input on keyboard
    def get_input(self):
        #get all pressed keys
        pressed_keys = pygame.key.get_pressed()
        #check if player is being delayed or not
        if self.delay != 0:
            if pygame.time.get_ticks() - self.last >= self.delay:
                    self.delay = 0
        else:
            if pressed_keys[pygame.K_UP]: self.propermove(movey=-1)
            elif pressed_keys[pygame.K_DOWN]: self.propermove(movey=1)
            elif pressed_keys[pygame.K_LEFT]: self.propermove(movex=-1)
            elif pressed_keys[pygame.K_RIGHT]: self.propermove(movex=1)
        
        #attack
        if pressed_keys[pygame.K_z]:
            #spawn attack sprite infront of player and check time values of how long active and cooldown
            now = pygame.time.get_ticks()
            if now - self.last_attack > ATTACK_RATE:
                self.set_delay(ATTACK_ACTIVE)
                self.last_attack = now
                Attack(self.game, Vector2(self.get_location().x, self.get_location().y)+self.facing*TILESIZE)
        
        #check interact. interact_holding is so player has to press it again to trigger
        if pressed_keys[pygame.K_x] and not self.interact_holding:
            self.interact_holding = True
            self.interact()
        
        if not pressed_keys[pygame.K_x]:
            self.interact_holding = False
                
        pressed_keys = 0
    
    #set delay value and update last delay time
    def set_delay(self, delay):
        if self.delay == 0:
            self.delay = delay
            self.last = pygame.time.get_ticks()
    
    #check if current location is equal to destination
    def checkpos(self):
        return self.destination.x != self.location.x or self.destination.y != self.location.y

    #set pos to destination. Used to make sure no left over decimals after smooth lerp to position
    def fixpos(self):
        self.location.x = self.destination.x
        self.location.y = self.destination.y

    #update player logic
    def update(self):
        #if not at destination lerp to it. Makes movement feel a bit better
        if self.destination.x != round(self.location.x,2) or self.destination.y != round(self.location.y,2):
            self.location.x = lerp(self.location.x, self.destination.x, 0.6)
            self.location.y = lerp(self.location.y, self.destination.y, 0.6)
        else:
            #fix the pos so no decimals
            if self.checkpos():
                self.fixpos()
            #can now get input
            self.get_input()
        
        TileCheckChangeable.check_night(self, self.destination.x, self.destination.y)
        #rotation has to use actual sprite image so must rotate based on if night or day or not
        if (not self.night):
            self.image = pygame.transform.rotate(self.game.player_img, self.rotation)
        else:
            self.image = pygame.transform.rotate(self.game.player_img_night, self.rotation)
        
        #sprite must always be a location because always moving
        self.rect = self.image.get_rect()
        self.rect.centerx = self.location.x * TILESIZE + TILESIZE/2
        self.rect.centery = self.location.y * TILESIZE + TILESIZE/2
        self.fix_check()

    #if player is hit
    def hit(self, hit):
        #bump back and remove some water
        self.pos_bump(dir_of_cols(hit.location, self.location),3, True)
        self.sub_water(WATER_AMOUNT)
    
    def add_water(self, amount):
        if (self.water_amount < MAX_WATER_AMOUNT):
            self.water_amount += amount
    
    def sub_water(self, amount):
        if (self.water_amount >= amount):
            self.water_amount -= amount
    
    def add_money(self, amount):
        self.money_amount += amount

#attack sprite (spawned when player attacks)
class Attack(pygame.sprite.Sprite):
    def __init__(self, game, loc):
        self.groups = game.all_sprites, game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.attack_img
        self.rect = self.image.get_rect()
        self.location = loc
        self.rect.center = self.location
        self.spawn_tick = pygame.time.get_ticks()

    #kill if exceded alive time
    def update(self):
        if pygame.time.get_ticks() - self.spawn_tick >= ATTACK_ACTIVE:
            self.kill()

#enemy logic basically health logic
class Enemy(pygame.sprite.Sprite):
    def update(self):
        if self.health <= 0:
            self.kill()
    def hit(self, player):
        self.health -= 1

#all map tiles in game all tiles will take after this basically where we need to set location pass in game value and check if night or not
class Tile(pygame.sprite.Sprite):
    def initialize(self, game):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.rect.centerx = self.location.x * TILESIZE + TILESIZE/2
        self.rect.centery = self.location.y * TILESIZE + TILESIZE/2
        self.game = game
        self.neighbors = []
        self.update_neighbors(game.map)
        self.night = False

    #used to get tiles from left and right, up and down needed for A* and spawning enemies
    def update_neighbors(self, gamemap):
	    if self.location.x < gamemap.mapheight - 1 and not self.layer_wall_check(gamemap.tiles[(self.location.x + 1,self.location.y)]):
            #we just need a basic tile to represent the location
	        self.neighbors.append(gamemap.tiles[(self.location.x + 1,self.location.y)][0])

	    if self.location.x > 0 and not self.layer_wall_check(gamemap.tiles[(self.location.x - 1,self.location.y)]):
		    self.neighbors.append(gamemap.tiles[(self.location.x - 1,self.location.y)][0])

	    if self.location.y < gamemap.mapheight - 1 and not self.layer_wall_check(gamemap.tiles[(self.location.x,self.location.y + 1)]):
		    self.neighbors.append(gamemap.tiles[(self.location.x,self.location.y + 1)][0])

	    if self.location.y > 0 and not self.layer_wall_check(gamemap.tiles[(self.location.x,self.location.y - 1)]):
		    self.neighbors.append(gamemap.tiles[(self.location.x,self.location.y - 1)][0])
    
    #check if any tile in any layer is a wall
    def layer_wall_check(self, tilestack):
        for tile in tilestack:
            if tile.is_wall():
                return True
        return False

    def is_wall(self): return False
    def is_enemy(self): return False
    def get_night(self): return self.night

    def __lt__(self, other): return False

class MoveableEnemy(Moveable, Enemy, TileCheckChangeable):
    #take game, enemy data (see global vars) and location
    def __init__(self, game, data, x, y):
        #all basic player stuff
        Moveable.__init__(self,game,Vector2(x,y))
        TileCheckChangeable.__init__(self, data)
        self.groups = game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.location.x * TILESIZE + TILESIZE/2
        self.rect.centery = self.location.y * TILESIZE + TILESIZE/2
        #random health is chosen
        self.health = random.randint(data.enemy.minhealth, data.enemy.maxhealth)
        #pathfinding is saved
        self.ai = data.enemy.ai
        #save speeed
        self.minspeed = data.enemy.minspeed
        self.maxspeed = data.enemy.maxspeed
        self.speed = random.randint(self.minspeed, self.maxspeed)
        #eating chance is set
        self.find_food_chance = random.randint(data.enemy.minflower, data.enemy.maxflower)
        #move back chance is set
        self.back_move_chance = random.randint(data.enemy.minweight, data.enemy.maxweight)
        # last location is the last tile lizard was on
        self.last_loc = self.location
        self.last = pygame.time.get_ticks()
        self.destination = Vector2(self.location.x, self.location.y)
        
        #blinking time and values
        self.last_blink = pygame.time.get_ticks()
        self.blink_img = self.get_img()
        self.is_blink = False

        #eat time and values
        self.eating = False
        self.last_eat = pygame.time.get_ticks()
        self.eat_time = data.enemy.eat_time
        self.what_is_lunch = self

        #what tiles the lizard is beside
        self.neighbors = []

    def move(self, movex=0, movey=0, ignorecols=False):  
        isnotgood = False
        if not ignorecols: isnotgood = self.check_blocks(movex, movey)
        if not isnotgood:
            self.destination.x += movex
            self.destination.y += movey
            self.update_neighbors(self.game.map)

    def checkpos(self):
        return self.destination.x != self.location.x or self.destination.y != self.location.y

    def fixpos(self):
        self.location.x = self.destination.x
        self.location.y = self.destination.y

    def update(self):
        #lerp movement so looks smooth
        if self.destination.x != round(self.location.x,2) or self.destination.y != round(self.location.y,2):
            self.location.x = lerp(self.location.x, self.destination.x, PLAYERSPEED)
            self.location.y = lerp(self.location.y, self.destination.y, PLAYERSPEED)
        else:
            if self.checkpos():
                self.fixpos()
        
        #set location and rotation
        TileCheckChangeable.check_night(self, round(self.location.x), round(self.location.y))
        #rotate image based on if night ot not
        self.image = pygame.transform.rotate(self.get_img(), self.rotation)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.location.x * TILESIZE + TILESIZE/2
        self.rect.centery = self.location.y * TILESIZE + TILESIZE/2
        self.fix_check()
        #check health
        Enemy.update(self)
        #get current time
        now = pygame.time.get_ticks()
        #move based on speed and if eating or not
        if (now - self.last > self.speed) and not self.eating:
            #get all neighbors
            self.update_neighbors(self.game.map)
            #randomly move to one of those neighbors
            new_loc = self.ai.Move(self.neighbors, self.last_loc, self.back_move_chance)
            #facing vector to be calculated into rotation
            facing = new_loc - self.location
            self.rotation = facing.angle_to(Vector2(0,-1))% 360
            #update last location and destination
            self.last_loc = Vector2(self.destination.x, self.destination.y)
            self.destination = new_loc
            #reset time
            self.last = now
            #reset speed
            self.speed = random.randint(self.minspeed, self.maxspeed)
            #lizard checks if on flower or sprout
            self.hungry()
        
        #is lizard eating right now
        if self.eating:
            self.eat()
            
    def hungry(self):
        #check if lizard actually wants to eat or just passin by
        ran_num = random.randint(0,100)
        if (ran_num <= self.find_food_chance):
            flower = self.check_flowers(0,0)
            sprout = self.check_sprouts(0,0)
            if flower:
                self.begin_eat(flower)
            elif sprout:
                self.begin_eat(sprout)
    
    def begin_eat(self, thing):
        #start blinking and count down until lizard has consumed tasty snack
        self.eating = True
        self.last_eat = pygame.time.get_ticks()
        self.last_blink = pygame.time.get_ticks()
        self.what_is_lunch = thing
    
    def eat(self):
        #blink the sprite
        self.blink()
        now = pygame.time.get_ticks()
        #check if eat time has elapsed if so reset values
        if now - self.last_eat > self.eat_time:
            self.eating = False
            if self.what_is_lunch == self: return
            self.what_is_lunch.kill()
            self.what_is_lunch = self
    
    #blink the sprite
    def blink(self):
        now = pygame.time.get_ticks()
        #switch back to empty sprite and normal sprite based on delay
        if now - self.last_blink > BLINK_DELAY:
            self.last_blink = pygame.time.get_ticks()
            if not self.is_blink:
                self.blink_img = self.get_img()
                self.image = self.game.empty_img
                self.is_blink = True
                return
            self.image = self.blink_img
            self.is_blink = False
    
    def hit(self, player):
        self.pos_bump(dir_of_cols(self.game.player.location, self.location),2)
        Enemy.hit(self, player)
    
    def update_neighbors(self, gamemap):
        #sanitize values to avoid errors
        if self.destination.x < 0 or self.destination.y < 0 or self.destination.x >= WIDTH/TILESIZE or self.destination.y >= HEIGHT/TILESIZE: return
        self.neighbors = []
        self.destination.x = round(self.destination.x)
        self.destination.y = round(self.destination.y)

        if self.destination.x < gamemap.mapheight - 1 and not self.layer_wall_check(gamemap.tiles[(self.destination.x + 1,self.destination.y)]):
            self.neighbors.append(gamemap.tiles[(self.destination.x + 1,self.destination.y)][0])
            
        if self.destination.x > 0 and not self.layer_wall_check(gamemap.tiles[(self.destination.x - 1,self.destination.y)]):
            self.neighbors.append(gamemap.tiles[(self.destination.x - 1,self.destination.y)][0])
        
        if self.destination.y < gamemap.mapheight - 1 and not self.layer_wall_check(gamemap.tiles[(self.destination.x,self.destination.y + 1)]):
            self.neighbors.append(gamemap.tiles[(self.destination.x,self.destination.y + 1)][0])
        
        if self.destination.y > 0 and not self.layer_wall_check(gamemap.tiles[(self.destination.x,self.destination.y - 1)]):
            self.neighbors.append(gamemap.tiles[(self.destination.x,self.destination.y - 1)][0])
    
    def check_flowers(self, x, y):
        for flower in self.game.flowers:
            if flower.location.x == round(self.destination.x) + x and flower.location.y == round(self.destination.y) + y:
                return flower
        return False
    
    def check_sprouts(self, x ,y):
        for sprout in self.game.sprouts:
            if sprout.location.x == round(self.destination.x) + x and sprout.location.y == round(self.destination.y) + y:
                return sprout
        return False
    
    def layer_wall_check(self, tilestack):
        for tile in tilestack:
            if tile.is_wall():
                return True
        return False

    #not used tried to stop them from stacking so much
    def layer_enemy_check(self, tilestack):
        for tile in tilestack:
            if tile.is_enemy():
                return tile
        return False

#normal tile that cant be planted on and changes based on day or night. All tiles basically follow this format
class NormalTile(Tile, Changeable):
    def __init__(self, data, x, y):
        Changeable.__init__(self, data)
        self.location = Vector2(x, y) #set location
        self.rect = self.image.get_rect() #set sprite location
    
    def initialize(self, game):
        #set groups and init tile, used when map script spawns tiles
        Tile.initialize(self, game)
        self.groups = game.all_sprites, game.changing_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)
    
class GrassTile(Tile, Changeable):
    def __init__(self, data, x, y):
        Changeable.__init__(self, data)
        self.location = Vector2(x, y)
        self.rect = self.image.get_rect()
    
    def initialize(self, game):
        Tile.initialize(self, game)
        self.groups = game.all_sprites, game.changing_tiles, game.plantable_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)

class WaterTile(Tile, Changeable, Enemy):
    def __init__(self, data, x, y):
        Changeable.__init__(self, data)
        self.location = Vector2(x, y)
        self.rect = self.image.get_rect()
    
    def initialize(self, game):
        Tile.initialize(self, game)
        self.groups = game.blocks, game.all_sprites, game.changing_tiles, game.enemies, game.non_enemy
        pygame.sprite.Sprite.__init__(self, self.groups)
    
    def is_wall(self): return True

    def hit(self, player):
        player.add_water(WATER_AMOUNT)
    
    def update(self): return


class ObstacleTile(Tile, Changeable):
    def __init__(self, data, x, y):
        Changeable.__init__(self, data)
        self.location = Vector2(x, y)
        self.rect = self.image.get_rect()

    def initialize(self, game):
        Tile.initialize(self, game)
        self.groups = game.blocks, game.all_sprites, game.changing_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)
    
    def is_wall(self): return True

class TreeTile(Tile, Enemy, Changeable):
    def __init__(self, data, x, y):
        Changeable.__init__(self, data)
        self.location = Vector2(x, y)
        self.rect = self.image.get_rect()

    def initialize(self, game):
        Tile.initialize(self, game)
        self.groups = game.blocks, game.enemies, game.non_enemy, game.all_sprites, game.changing_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.health = 6
    
    def is_wall(self): return True

#lizard spawner!
class CaveTile(Tile, Changeable):
    def __init__(self, data, x, y):
        Changeable.__init__(self, data)
        self.location = Vector2(x, y)
        self.rect = self.image.get_rect()
        #set spawn chances
        self.day_chances = ENEMY_DAY_CHANCE
        self.night_chances = ENEMY_NIGHT_CHANCE

    def initialize(self, game):
        Tile.initialize(self, game)
        self.groups = game.blocks, game.all_sprites, game.changing_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)
    
    #spawn lizards when day/night line crosses
    def line_hit(self):
        if self.colliding: return
        Changeable.line_hit(self)
        if self.night:
            self.spawn_enemy(self.night_chances)
        else:
            self.spawn_enemy(self.day_chances)

    def spawn_enemy(self, chances):
        #check enemy cap
        if self.maxed(): return
        #for all chances
        for num in chances:
            loc = self.get_spawn_loc()
            #check to spawn enemy
            if random.randint(0,100) <= num:
                #check enemy cap
                if self.maxed(): return
                #set up enemy weight list basically an list will all relavent lizards duplicated by their weight
                pool = []
                for data in self.game.enemy_data:
                    pool += [data]*data.enemy.spawn_weight
                MoveableEnemy(self.game, random.choice(pool), loc.x, loc.y)
    
    #subtract non enemies and increase limit based on amount of flowers and sprouts
    def maxed(self):
        return len(self.game.enemies) - len(self.game.non_enemy) >= (MAX_ENEMY_LIMIT + (len(self.game.sprouts)+len(self.game.flowers))//FLOWER_AMOUNT_DIVIDE)

    #get random lizard used to be used when did not have weights
    def get_ran_pick(self):
        return random.randint(0,len(self.game.enemy_data)-1)

    #get spawn location based random tile selected from all neighbors
    def get_spawn_loc(self):
        return self.neighbors[random.randint(0,len(self.neighbors)-1)].location
    
    def is_wall(self): return True

class Flower(Tile, DayHits, SellHits, TileCheckChangeable):
    def __init__(self, game, flower_data, x, y, is_day):
        TileCheckChangeable.__init__(self, flower_data, is_day)
        DayHits.__init__(self)
        SellHits.__init__(self)
        self.data = flower_data
        self.groups = game.all_sprites, game.sprouts, game.changing_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.location = Vector2(x, y)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.location.x * TILESIZE + TILESIZE/2
        self.rect.centery = self.location.y * TILESIZE + TILESIZE/2
        self.game = game

        #flower related data
        self.is_sprout = True
        self.watered = False
        #how many day/night line passes
        self.maturity_count = 0
        #how many sell line passes
        self.sellability_count = 0
        #is being held
        self.held = False
        #is a flower
        self.mature = False
        #being held by what defaults to player
        self.holder = self.game.player
        #set random price
        self.amount = random.randint(SELL_BASE_AMOUNT,SELL_MAX_AMOUNT)

        #blink values
        self.last = pygame.time.get_ticks()
        self.is_blink = False
        self.blink_img = self.image

    def update(self):
        TileCheckChangeable.check_night(self, round(self.location.x), round(self.location.y), self.is_blink)
        #if being held have to update location and blink
        if self.held:
            self.location = self.holder.location + self.holder.facing
            self.rect = self.image.get_rect()
            self.rect.centerx = self.location.x * TILESIZE + TILESIZE/2
            self.rect.centery = self.location.y * TILESIZE + TILESIZE/2
            self.blink()
    
    #same as lizards
    def blink(self):
        now = pygame.time.get_ticks()
        if now - self.last > BLINK_DELAY:
            self.last = pygame.time.get_ticks()
            if not self.is_blink:
                self.blink_img = self.image
                self.image = self.game.empty_img
                self.is_blink = True
                return
            self.image = self.blink_img
            self.is_blink = False

    #change sprite when day/night line hits and update maturity
    def line_hit(self):
        if self.colliding: return
        DayHits.line_hit(self)
        if self.held: return
        if self.maturity_count < TILL_MATURE:
            self.maturity_count += 1
        elif not self.mature:
            #sprout is now flower
            #if not watered plant has died
            if (not self.watered):
                self.kill()
                return
            self.mature = True
            #change to flower group
            self.game.sprouts.remove(self)
            self.game.flowers.add(self)
            #update images
            TileCheckChangeable.change_day_night_image(self, self.data.flower_image, self.data.flower_image_night)
    
    #update images if watered and set watered value
    def water(self):
        if not self.watered:
            TileCheckChangeable.change_day_night_image(self, self.data.watered_image, self.data.watered_image_night)
            self.watered = True
    
    #set values for when being held
    def hold(self, holder):
        self.sellability_count = 0
        self.held = True
        self.holder = holder
        self.game.holding.add(self)
        self.last = pygame.time.get_ticks()
        self.game.flowers.remove(self)

    #drop flower and set location properly
    def drop(self):
        self.held = False
        self.is_blink = False
        self.holder = self.game.player
        self.location = self.holder.location + self.holder.facing
        self.rect = self.image.get_rect()
        self.rect.centerx = round(self.location.x) * TILESIZE + TILESIZE/2
        self.rect.centery = round(self.location.y) * TILESIZE + TILESIZE/2
        self.game.holding.remove(self)
        self.game.flowers.add(self)
    
    #check sell line quota
    def sell_hit(self):
        if self.sell_colliding: return
        SellHits.sell_hit(self)
        if not self.held:
            self.sellability_count += 1
            if self.sellability_count >= TILL_SELL:
                self.sell(self.game.player)
    
    #when flower is sold kill and update player's money
    def sell(self, player):
        player.add_money(self.amount)
        self.kill()
    
    def get_location(self):
        return Vector2(round(self.location.x) * TILESIZE + TILESIZE/2, round(self.location.y) * TILESIZE + TILESIZE/2)

#for tiles that only exist at day time
class DayOnlyTile(Tile, DayHits):
    def __init__(self, data, x, y):
        DayHits.__init__(self)
        self.image = data.daytile
        self.location = Vector2(x, y)
        self.rect = self.image.get_rect()
        self.night = False

    def initialize(self, game, groups=False):
        Tile.initialize(self, game)
        if groups:
            self.groups = groups
        else:
            self.groups = game.all_sprites, game.changing_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)

    def line_hit(self):
        if self.colliding: return
        if self.night:
            for group in self.groups:
                if group == self.game.changing_tiles: continue
                group.add(self)
            self.night = False
        else:
            for group in self.groups:
                group.remove(self)
            self.game.changing_tiles.add(self)
            self.night = True
        self.colliding = True


class ShopableTile(DayOnlyTile):
    def __init__(self, data, x, y):
        DayOnlyTile.__init__(self, data, x, y)
    
    def initialize(self, game):
        DayOnlyTile.initialize(self, game, (game.all_sprites, game.shopable, game.changing_tiles))

class ShopkeeperTile(DayOnlyTile):
    def __init__(self, data, x, y):
        DayOnlyTile.__init__(self, data, x, y)
    
    def initialize(self, game):
        DayOnlyTile.initialize(self, game, (game.all_sprites, game.blocks, game.changing_tiles))