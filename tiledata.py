'''
This file converts the numbers grabbed from the map csvs and turns them into relevent tile objects.
This is so tiles can be added with ease
'''
import pygame
from os import path
from sprites import *

class Normal:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, img + 'n.png')).convert_alpha()
    
    def make(self, x, y):
        return NormalTile(self, x, y)

class Grass:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, img + 'n.png')).convert_alpha()
    
    def make(self, x, y):
        return GrassTile(self, x, y)

class Water:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, img + 'n.png')).convert_alpha()
    
    def make(self, x, y):
        return WaterTile(self, x, y)

class Obstacle:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, img + 'n.png')).convert_alpha()
    
    def make(self, x, y):
        return ObstacleTile(self, x, y)

class Tree:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, img + 'n.png')).convert_alpha()
    
    def make(self, x, y):
        return TreeTile(self, x, y)

class Cave:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, img + 'n.png')).convert_alpha()
    
    def make(self, x, y):
        return CaveTile(self, x, y)

class DaySpawn:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()

    def make(self, x, y):
        return DayOnlyTile(self, x, y)

class Shopable:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()

    def make(self, x, y):
        return ShopableTile(self, x, y)

class Shopkeeper:
    def __init__(self, img, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()

    def make(self, x, y):
        return ShopkeeperTile(self, x, y)

class Flower:
    def __init__(self, img, sproutimg, wateredimg, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, sproutimg + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, sproutimg + 'n.png')).convert_alpha()
        self.flower_image = pygame.image.load(path.join(imgfolder, img + '.png')).convert_alpha()
        self.flower_image_night = pygame.image.load(path.join(imgfolder, img + 'n.png')).convert_alpha()
        self.watered_image = pygame.image.load(path.join(imgfolder, wateredimg + '.png')).convert_alpha()
        self.watered_image_night = pygame.image.load(path.join(imgfolder, wateredimg + 'n.png')).convert_alpha()

class EnemyData:
    def __init__(self, enemy, imgfolder):
        self.daytile = pygame.image.load(path.join(imgfolder, enemy.img + '.png')).convert_alpha()
        self.nighttile = pygame.image.load(path.join(imgfolder, enemy.img + 'n.png')).convert_alpha()
        self.enemy = enemy


#all the tiles by number
def get_tile_data(imgfolder):
    return {
        "-1":None,
        "0":Grass('grass1', imgfolder),
        "1":Grass('grass2', imgfolder),
        "2":Grass('grass3', imgfolder),
        "3":Grass('grass4', imgfolder),
        "4":Water('river1', imgfolder),
        "5":Water('river2', imgfolder),
        "9":Obstacle('wall', imgfolder),
        "10":Water('water1', imgfolder),
        "11":Water('waterwall1', imgfolder),
        "12":Water('waterwall2', imgfolder),
        "13":Water('waterwall3', imgfolder),
        "14":Water('waterwall4', imgfolder),
        "15":Water('waterwall6', imgfolder),
        "16":Water('waterwall5', imgfolder),
        "17":Water('waterwall7', imgfolder),
        "18":Water('waterwall8', imgfolder),
        "19":Tree('tree1', imgfolder),
        "20":Tree('tree2', imgfolder),
        "21":Tree('tree3', imgfolder),
        "22":Shopkeeper('merchant', imgfolder),
        "24":Normal('mat1', imgfolder),
        "25":Normal('mat2', imgfolder),
        "26":Normal('mat3', imgfolder),
        "27":Shopable('package', imgfolder),
        "28":Cave('cave', imgfolder),
        "30":DaySpawn('50', imgfolder),
        "31":DaySpawn('arrow', imgfolder),
        "32":Normal('ground1', imgfolder),
        "33":Normal('ground2', imgfolder),
        "34":Normal('ground3', imgfolder),
        "35":Normal('ground4', imgfolder),
        "36":Obstacle('rock', imgfolder),
        "45":Obstacle('table', imgfolder),
        "46":Water('waterwall1g', imgfolder),
        "47":Water('waterwall2g', imgfolder),
        "48":Water('waterwall3g', imgfolder),
        "49":Water('waterwall4g', imgfolder),
        "50":Water('waterwall5g', imgfolder),
        "51":Water('waterwall6g', imgfolder),
        "52":Water('waterwall7g', imgfolder),
        "53":Water('waterwall8g', imgfolder),
        "54":Normal('sellmat2', imgfolder),
        "55":Normal('sellmat3', imgfolder),
        "56":Normal('sellmat4', imgfolder),
        "57":Normal('sellmat5', imgfolder),
        "58":Normal('sellmat6', imgfolder),
        "59":Normal('sellmat7', imgfolder),
        "60":Normal('sellmat8', imgfolder),
        "61":Normal('sellmat1', imgfolder),
        "63":Normal('sellmat9', imgfolder),
    }

#get all the data objects relating to flowers
def get_flower_data(imgfolder):
    flowers = []
    for flower in FLOWERS:
        flowers.append(Flower(flower, SPROUT, SPROUT_WATERED, imgfolder))
    return flowers

#get all the data objects relating to enemies
def get_enemy_data(imgfolder):
    enemies = []
    for enemy in ENEMIES:
        enemies.append(EnemyData(enemy,imgfolder))
    return enemies