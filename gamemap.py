'''
This script handles rendering and generating map data based on map csvs
'''
import pygame, csv
from os import path
from pygame.locals import *
from globalvars import *
from tiledata import *

#turn csv file into list
def read_csv(file):
    with open(file) as csv_file:
        return list(csv.reader(csv_file, delimiter=','))

#this was used for test map left in in for testing
class Map:
    def __init__(self, file):
        self.map_data = []
        with open(file, 'rt') as file:
            for line in file:
                self.map_data.append(line.rstrip())
        self.mapwidth = len(self.map_data[0])
        self.mapheight = len(self.map_data)
        self.width = self.mapwidth * TILESIZE
        self.height = self.mapwidth * TILESIZE

#the real map loader
class MainMap:
    def __init__(self, mapfolder, imgfolder):
        #get lists of maps based on all the map csvs. Multiple csvs are used for layers. First in list is rendered first and so on
        self.map_layers = []
        for layer in MAPLAYERS:
            self.map_layers.append(read_csv(path.join(mapfolder, layer)))

        #save sizes of map
        self.mapwidth = len(self.map_layers[0][0])
        self.mapheight = len(self.map_layers[0])
        self.width = self.mapwidth * TILESIZE
        self.height = self.mapwidth * TILESIZE
        #save dictionary of numbers to tiles
        self.tile_gid = get_tile_data(imgfolder)
        #all map tiles and locations will be saved here
        self.tiles = dict()
        #the number of layers i.e different csvs the map has
        self.num_layers = len(self.map_layers)
    
    '''
    this takes all the raw data gotten from csvs, generates the tiles based on the tile data dictionary.
    '''
    def render(self, surface):
        for layer in self.map_layers:
            for row, tiles in enumerate(layer):
                for col, tile in enumerate(tiles):
                    #check if -1 tile i.e no tile
                    if int(tile) >= 0:
                        #make the tile based on data folder
                        new_tile = self.tile_gid[tile].make(col,row)
                        #check if tile exists at same location and if to append to already existing tile stack
                        if (col,row) in self.tiles:
                            self.tiles[(col,row)].append(new_tile)
                        else:
                            self.tiles[(col,row)] = [new_tile]
    
    #used to blit the tiles on a surface but i just handle that in the sprites file now. Left it in though incase I want to switch.
    def make_map(self):
        tmp_surf = pygame.Surface((self.width, self.height))
        self.render(tmp_surf)
        return tmp_surf
    
    #initialize all tiles of map (basically spawn them!)
    def initialize(self, game):
        for tilelayer in self.tiles.values():
            for tile in tilelayer:
                tile.initialize(game)