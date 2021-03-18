'''
This file handles holding all heavily tweaked values in an easily refrenced scripts. Global vars are bad practice but saved a lot of time in my case
'''
import pygame, math

from enum import Enum
from pathfinding import *

#Vector2 function just simplified call to use pygame's vector2
Vector2 = pygame.math.Vector2

#lerping two values
def lerp(y1, y2, mu):
    return(y1*(1-mu)+y2*mu)

#get tiled direction of collision based on two vectors
def dir_of_cols(destv, origv):
    deg = math.atan2(destv.x-origv.x, destv.y-origv.y)/math.pi*180
    if deg < 0:
        deg_final = 360 + deg
    else:
        deg_final = deg
    return(DIRECTIONDEFS[round(deg_final/45)])

#basic colours
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (75, 0, 130)
FIELD = (128, 161, 66)
WATER_COL = (28,163,236)
YELLOW = (255, 255, 0)

#game states
class GameState(Enum):
    QUIT = -1
    TITLE = 0
    INFO = 1
    PLAYING = 2

#game relevent data
WIDTH = 960
HEIGHT = 960
FPS = 60
BACKCOLOUR = FIELD

TILESIZE = 24
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

#images for start of game
TITLE_IMG = 'title.png'
INFO_IMG = 'info.png'

#player values
PLAYER_IMG = 'player.png'
PLAYER_IMG_NIGHT = 'playern.png'
#amount movement is lerped
PLAYERSPEED = 0.8

#attack values
ATTACK_IMG = "attack.png"
ATTACK_ACTIVE = 100
ATTACK_RATE = 500

WALL_IMG = "wall.png"

#data for when sprites blink
EMPTY_IMG = "empty.png"
BLINK_DELAY = 250

#direction list for getting direction of collisions
DIRECTIONDEFS = [(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]

#map data. spawned in based on order
MAPLAYERS = ['flowerplant_Ground.csv', 'flowerplant_Trees.csv', 'flowerplant_Shop.csv', 'flowerplant_Spawners.csv']

#LINES
DAY_SPEED = 0.1
SELL_SPEED = 0.1
SELL_LENGTH = 0.115

#ENEMIES
#enemy class has a lot of values used for randomness to give lizards some personality. 
class ENEMY_INSTANCE:
    def __init__(self, img, ai, minhealth, maxhealth, minweight, maxweight, minspeed, maxspeed, minflower, maxflower, eat_time, spawn_weight):
        #image of the lizard
        self.img = img
        #what pathfinding it uses
        self.ai = ai
        #minimum chance to go backwards
        self.minweight = minweight
        #maximum chance to go backwards
        self.maxweight = maxweight
        #minimum chance to eat a flower when on top
        self.minflower = minflower
        #maximum chance to eat a flower when on top
        self.maxflower = maxflower
        #minimum hits to die
        self.minhealth = minhealth
        #maximum hits to die
        self.maxhealth = maxhealth
        #minimum speed chance (makes the lizards look like they are deciding to chill or move)
        self.minspeed = minspeed
        #maximum speed chance
        self.maxspeed = maxspeed
        #how long it takes to eat a flower
        self.eat_time = eat_time
        #how likley the spawner will choose this type of lizard
        self.spawn_weight = spawn_weight

#create types of enemies
ENEMIES = [ENEMY_INSTANCE('lizard', RandomFinding(), 2, 4, 80, 100, 1000, 3000, 65, 100, 2000, 95), 
           ENEMY_INSTANCE('lizardfast', RandomFinding(), 4, 6, 80, 100, 500, 600, 80, 100, 1000, 5)]
#amount and chance of spawning on day pass
ENEMY_DAY_CHANCE = [20]
#amount and chance of spawning on night pass
ENEMY_NIGHT_CHANCE = [90, 60, 20]
#maximum enemies allowed
MAX_ENEMY_LIMIT = 20
#what amount of flowers is dividedby and then added to max_enemy_limit
FLOWER_AMOUNT_DIVIDE = 8

#WATER
WATER_AMOUNT = 10
MAX_WATER_AMOUNT = 100

#MARKET
STARTING_CASH = 150
SEED_PRICE = 50
AMOUNT_OF_SEED = 1

#SPROUTS
SPROUT = 'sprout'
SPROUT_WATERED = 'sproutw'

#FLOWERS
FLOWERS = ['flower1', 'flower2', 'flower3', 'flower4', 'flower5', 'flower6', 'flower7', 'flower8']
SELL_BASE_AMOUNT = 100
SELL_MAX_AMOUNT = 250
#amount of maturity passes
TILL_MATURE = 1
#amount of sell passes
TILL_SELL = 2