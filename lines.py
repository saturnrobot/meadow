import pygame, random, math
from pygame.locals import *
from globalvars import *

class RotatingLine:
     ### Intervals Example ###
    # An "intervals" variable of [ (0.00, 0.50), (0.75, 1.00) ] represents a line with a gap
    # starting halfway through the line, the gap is 25% of the length of the line, followed by
    # the remaining 25% being a collidable line.

    def __init__(self, origin, angle, intervals, speed, draw=True, colour=BLACK, thicc=0):
        self.origin = origin        # This is the origin point that the line will rotate around
        self.angle = angle          # This is the initial angle that the line will face, in degrees
        self.intervals = intervals  # This is a list of tuples representing the visible segments that create gaps
        self.speed = speed          # Speed of the lines rotation
        self.draw = draw            # if to show the line or not
        self.colour = colour        # colour of line
        self.segments = []          # Represents the actual segments we'll draw, handled in update
        self.thicc = thicc          # if line is rendered as aaline or line with thickness

    def render(self, screen):
        # draw each of the rotating line segments
        for seg in self.segments:
            if self.draw:
                if self.thicc <= 0:
                    pygame.draw.aaline(screen, self.colour, seg[0], seg[1])
                else:
                    pygame.draw.line(screen, self.colour, seg[0], seg[1], self.thicc)

    def rotate(self, deg=1):
        # Rotate the line by 1 degree
        # Return TRUE if the line reset to 90 degrees, FALSE otherwise
        reset = False

        # increase the angle of the rotating line
        self.angle = (self.angle + deg)

        # the rotating line angle ranges between 90 and 180 degrees
        #if self.angle > 180:
            # when it reaches an angle of 180 degrees, reset it 
            #self.angle = 90
            #reset = True

        self._update_line_segments()
    
        return reset

    def _update_line_segments(self):
        # This function is going to set up the coordinates for the enpoints
        # of each "segment" of our line.

        # The points associated with each line segment must be recalculated as the angle changes
        self.segments = []
        
        # consider every line segment length
        for partial_line in self.intervals:
            # compute the start of the line...
            sol_x = self.origin[0] + math.cos(math.radians(self.angle)) * WIDTH * partial_line[0]
            sol_y = self.origin[1] + math.sin(math.radians(self.angle)) * WIDTH * partial_line[0]
            
            # ...and the end of the line...
            eol_x = self.origin[0] + math.cos(math.radians(self.angle)) * WIDTH * partial_line[1]
            eol_y = self.origin[1] + math.sin(math.radians(self.angle)) * WIDTH * partial_line[1]
            
            # ...and then add that line to the list
            self.segments.append( ((sol_x, sol_y), (eol_x, eol_y)) )
