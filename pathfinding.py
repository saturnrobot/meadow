'''
This file handles path finding logic for enemies
'''
import random

#was going to try and do Astar but gave up :(
class Astar:
    def h_score(self, tile1, tile2):
        tile1loc = tile1.location
        tile2loc = tile2.location
        return abs(tile1loc.x - tile2loc.x) + abs(tile1loc.y - tile2loc.y)

#random based movement 
class RandomFinding:
    def Move(self, tiles, last_loc, weight):
        #checks if only one movement option
        if len(tiles) <= 1: return last_loc
        #return tiles[random.randint(0,len(tiles)-1)].location
        self.final_tiles = tiles
        last_tile = tiles[0]
        #remove last visited tile from list (allows for better spread of lizards)
        for i in range(len(self.final_tiles)):
            if self.final_tiles[i].location == last_loc:
                last_tile = self.final_tiles.pop(i)
                break
        random_choice = random.randint(0,100)
        #check lizard moveback chance against value and then either move to new tile or last visited one
        if weight >= random_choice:
            return self.final_tiles[random.randint(0,len(self.final_tiles)-1)].location
        return last_tile.location