import pyscreenshot as PSS
import sys

class Vision:

    @property
    def edge_coords(self):
        """ Returns a tuple: (left, top) """
        return self._edge_coords

    @property
    def dimens_pix(self):
        """ Returns a tuple: (width, height) in pixels"""
        return self._dimens_pix

    @property
    def dimens_blx(self):
        """ Returns a tuple: (width, height) in number of blocks """
        return self._dimens_blx

    @property
    def vis_filename(self):
        return "vis_mem.png"

    def get_reset(self):
        # HARDCODING the coordinates of the smiley face
        assert not self is None
        assert not self._dimens_pix is None
        assert not self._edge_coords is None
        (wpix,hpix) = self._dimens_pix
        (xpix,ypix) = self._edge_coords
        ynew = ypix - 20
        xnew = xpix + (wpix / 2)
        return (xnew, ynew)

    def screen_grab(self):
        (left,top) = self._edge_coords
        (width,height) = self._dimens_pix
        right = left + width
        bottom = top + height
        vis = PSS.grab((left,top,right,bottom))
        vis.save(self.vis_filename) # optional, delete later for optimization
        return vis

    def __init__(self, size):
        # HARD CODING the coordinates of things to get logic down before
        # attempting to automate vision    
        """ beginner: h144|w144|l428|wlr:.80
        intermediate: h256|w256|l428|wlr:.40
        expert: h256|w480|l419|wlr: """
        height = 0
        width = 0
        left = 0
        if size == 1:
            height = 144
            width = 144
            left = 424
        elif size == 2:
            height = 256
            width = 256
            left = 424
        elif size == 3:
            height = 256
            width = 480
            left = 414
        top = 166
        self._edge_coords = (left, top)
        self._dimens_pix = (width, height)
        self._dimens_blx = (width/16, height/16)
        self.screen_grab() # so that when I start, I know that screen is
                          # calibrated
        print " > Screen grabbed at", self.vis_filename

    def init_grid(self):
        # HARD CODING initial grid is a brand new grid
        y,x = self._dimens_blx
        return [[1 for i in range(x)] for i in range(y)], self._dimens_blx

    """ Identifies the state of a single block. Should only be used when checking
    the status of a block after being clicked, not for scanning the entire board 
    after the first click """
    def identify(self,x,y):
        (l0,t0) = self.edge_coords
        (l1,t1) = (l0 + x * 16, t0 + y * 16)
        (r1,b1) = (l1 + 16, t1 + 16)
        vis = PSS.grab((l1,t1,r1,b1))
        #vis.save("a_single_block.png")
        vispix = vis.load()
        print vispix[8,8] #8,8 distinguishes between 1,2,3,4,5,6 for sure

    def labelxy(self,x,y,board):
        colors = {(189,189,189) : 0,
                  (0,0,255)        : -1,
                  (0,123,0)        : -2,
                  (255,0,0)        : -3,
                  (0,0,123)        : -4,
                  (123,0,0)        : -5,
                  (0,123,123)    : -6,
                  (0,0,0)        : 8}
        (x1,y1) = (x * 16 + 8, y * 16 + 8)
        rgb = board[x1,y1]
        try:
            return colors[rgb]
        except KeyError:
            print board[x1,y1],"not found"
            #sys.exit()
            return None
