import sys
import time
from eyes import Vision
from mouse import Mouse
from itertools import izip
from pykeyboard import PyKeyboard as PK

""" Invariant: OSIMS does not ever deal with pixels. Vision keeps track of all
the pixel coordinates of every significant feature. Mouse is initialized with 
Vision """
class OSIMS:

    @property
    def puzzle_size(self):
        return self._puzzle_size

    @property
    def vis(self):
    	""" Returns the Vision instance that tracks the state of the screen """
    	return self._vis

    @property
    def keys(self):
    	return self._keys

    @property
    def mse(self):
    	return self._mse

    @property
    def board(self):
    	return self._board

    @property
    def check_queue(self):
    	return self._check_queue

    @property
    def safe_queue(self):
    	return self._safe_queue
    
    @property
    def revisit_queue(self):
    	return self._revisit_queue

    @property
    def guess_queue(self):
    	return self._guess_queue

    def print_board(self):
    	assert not self.board is None
    	print "The current state of the board: "
    	for i in range(len(self.board)):
    		for j in range(len(self.board[i])):
    			d = self.board[i][j]
    			if d >= 0:
    				print "",
    			print d,
    		print ""

    """ HELPER FUNCTION to initiate profiling on all blocks adjacent to block
    at x,y """ 	
    def prof_perim(self,x,y,brd_img):
    	for i in self._surround:
    		xf,yf = self._addtups(i,(x,y))
    		self.profile(xf,yf,brd_img)

    def enqueue_init(self,x,y,nil):
    	self.check_queue.append((x,y))
    	return True
    
    def kill(self,x,y,nil):
    	print " > Unexpected color, check log"
    	return False
    
    def lose(self,x,y,nil):
    	print " > Got a mine...woops!"
    	return False

    def del_later(self,x,y,nil):
    	self.keys.tap_key('Return')
    	return False

    def profile(self, x, y, brd_img):
    	maxx, maxy = self.vis.dimens_blx
    	if x >= maxx or y >= maxy or x < 0 or y < 0:
    		#print "Profiling out of bound"
    		return True
    	#First check if block at x,y already has information. If so, then return
    	if self.board[x][y] != 1:
    		return True
    	label = self.vis.labelxy(x,y,brd_img)
    	self.board[x][y] = label
        results = {0 : self.prof_perim,
    				-1 : self.enqueue_init,
    				-2 : self.enqueue_init,
    				-3 : self.enqueue_init,
    				-4 : self.enqueue_init,
    				-5 : self.enqueue_init,
    				-6 : self.enqueue_init,
    				8 : self.lose,
    				None: self.del_later}
    	return results[label](x,y,brd_img)

    def mark_mines(self):
    	maxx, maxy = self.vis.dimens_blx
    	while self.check_queue != []:
    		x,y = self.check_queue.pop()
    		unknowns = []
    		label = self.board[x][y]
    		for i in self._surround:
    			xf,yf = self._addtups(i,(x,y))
    			if xf >= maxx or yf >= maxy or xf < 0 or yf < 0:
    				pass
    			elif self.board[xf][yf] == 1 or self.board[xf][yf] == 8:
    				unknowns.append((xf,yf))
    		# if the number of unknowns adjacent to a block is equal to the 
    		# number of mines adjacent to the block, then those unknowns must 
    		# be mines, so all we can do is register those blocks as mines
    		if len(unknowns) == abs(label):
    			for x,y in unknowns:
    				if self.board[x][y] != 8:
    					self.mse.right_click(x,y)
    					if (x,y) in self.guess_queue:
    						self.guess_queue.remove((x,y))
    					self.board[x][y] = 8
    					self._mine_count += 1
    		else: #need to check later for adjacent safes, store in queue
    			self.revisit_queue.append((x,y))

    def determine_safes(self):
    	maxx, maxy = self.vis._dimens_blx
    	while self.revisit_queue != []:
    		x,y = self.revisit_queue.pop()
    		unknowns = []
    		mines = []
    		label = self.board[x][y]
    		for i in self._surround:
    			xf,yf = self._addtups(i,(x,y))
    			if xf >= maxx or yf >= maxy or xf < 0 or yf < 0:
    				pass
    			elif self.board[xf][yf] == 1:
    				unknowns.append((xf,yf))
    				if not (xf,yf) in self.guess_queue:
    					 self.guess_queue.append((xf,yf))
    			elif self.board[xf][yf] == 8:
    				mines.append((xf,yf))
    				unknowns.append((xf,yf))
    		# if the number of known mines is equal to the label of the block, 
    		# then any unknowns adjacent to the mine must be safe, so click them
    		if len(mines) == abs(label):
    			for xu,yu in unknowns:
    				if (not ((xu,yu) in self.safe_queue)) and not (xu,yu) in mines:
    					self.safe_queue.append((xu,yu))
    		else:
    			self.check_queue.append((x,y))

    def do_clicks(self):
    	if self.safe_queue == []:
    		if self.check_queue == []: # Game is done
    			print " > Ran out of things to check! :)"
    			return False
    		else: # Ran out of safe_clicks
                        print " > Nothing sure, making a guess"
    			x,y = self.guess_queue.pop(0)
    			#time.sleep(0.75)
    			self.mse.left_click(x,y)
    			time.sleep(0.1)
    			board_img = self.vis.screen_grab().load()
    			output = self.profile(x,y,board_img)
    			return output 
    	else:
    		for x,y in self.safe_queue:
    			self.mse.left_click(x,y)
    		time.sleep(0.1) # Necessary so game updates fast enough for
    						# screen grab to catch it 0.1 is reasonably slow
    		board_img = self.vis.screen_grab().load()
    		while self.safe_queue != []:
    			x,y = self.safe_queue.pop()
    			try:
    				#print "removed",x,y,"from guess_queue"
    				self.guess_queue.remove((x,y))
    			except:
    				print x,y,"not in guess_queue"
    				pass
    			self.profile(x,y,board_img)
    		return True

    """ Resets the board, then makes a click, then profiles the new board """
    def kickoff(self):
    	x, y = self.vis.dimens_blx
    	#Reseting the game board
    	self.mse.reset_board()
    	
    	#Making the first click
    	mid_x = x/2
    	mid_y = y/2 
    	self.mse.left_click(mid_x,mid_y)
    	time.sleep(0.1)
    	board_img = self.vis.screen_grab().load()
    	self.profile(mid_x, mid_y, board_img)
    	self.mark_mines()
    	self.determine_safes()
        print "we think the dimensions are", x, y
    	while self.do_clicks():
    		self.mark_mines()
    		self.determine_safes()
        if self.puzzle_size == 1:
            return self._mine_count == 10
        elif self.puzzle_size == 2:
            return self._mine_count == 40
    	return self._mine_count == 99
    	"""if self._mine_count == 40:
    		print "We won!"
    		#PK().tap_key('Return')
    		return True
    	else:
    		print " > check here"
    		return False """

    def refresh(self):
    	self._mine_count = 0
    	self._check_queue = []
    	self._safe_queue = []
    	self._revisit_queue = []
    	self._guess_queue = []
    	(self._board,size) = self._vis.init_grid()

    def run(self, cont):
    	wins = 0
    	total = 0
    	self.refresh()
    	i = 0
    	while i < cont:
    		if self.kickoff():
    			wins += 1
    			#sys.exit()
    			time.sleep(0.5)
    			self.keys.tap_key("Return")
                        time.sleep(0.5)
    		total += 1
    		i += 1
    		print wins,"wins of",total,"total"
    		self.refresh()
    
    def __init__(self):
    	print " > Initiated"
        if len(sys.argv) < 3:
            print "Need to pass in args: python OSIMS <#times> <size>"
            print "where size is defined as: 1 = beginner, 2 = intermediate, 3 = expert"
            return

     	times = int(sys.argv[1])
        self._puzzle_size = int(sys.argv[2])
   	self._vis = Vision(self._puzzle_size)
    	self._mse = Mouse(self._vis)
    	self._keys = PK()
    	self._addtups = lambda xs,ys: tuple(x+y for x,y in izip(xs,ys))
    	self._surround = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    	self.refresh()
    	print " > Grid identified of dimensions", self.vis.dimens_blx
    	self.run(times)
