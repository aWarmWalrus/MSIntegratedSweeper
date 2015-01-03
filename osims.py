import time
from eyes import Vision
from mouse import Mouse
from itertools import izip
from pymouse import PyMouse as PM
from pykeyboard import PyKeyboard as PK

""" Invariant: OSIMS does not ever deal with pixels. Vision keeps track of all
the pixel coordinates of every significant feature. Mouse is initialized with 
Vision """
class OSIMS:

	@property
	def vis(self):
		""" Returns the Vision instance that tracks the state of the screen """
		return self._vis

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

	def print_board(self):
		assert not self.board is None
		print "The current state of the board: "
		for i in range(len(self.board)):
			for j in range(len(self.board[i])):
				d = self.board[j][i]
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
	
	def bull(self,x,y,nil):
		pass

	def profile(self, x, y, brd_img):
		maxx, maxy = self.vis.dimens_blx
		if x >= maxx or y >= maxy or x < 0 or y < 0:
			return
		#First check if block at x,y already has information. If so, then return
		if self.board[x][y] != 1:
			return
		label = self.vis.labelxy(x,y,brd_img)
		self.board[x][y] = label
		results = {0 : self.prof_perim,
					-1 : self.enqueue_init,
					-2 : self.enqueue_init,
					-3 : self.enqueue_init,
					-4 : self.enqueue_init,
					-5 : self.enqueue_init,
					-6 : self.enqueue_init,
					None: self.bull}
		results[label](x,y,brd_img)

	def mark_mines(self):
		maxx, maxy = self.vis.dimens_blx
		while self.check_queue != []:
			x,y = self.check_queue.pop()
			unknowns = []
			label = self.board[x][y]
			for i in self._surround:
				xf,yf = self._addtups(i,(x,y))
				if xf >= maxx or yf >= maxy or xf < 0 or yf < 0:
					unknowns = unknowns
				elif self.board[xf][yf] == 1 or self.board[xf][yf] == 8:
					unknowns.append((xf,yf))
			# if the number of unknowns adjacent to a block is equal to the 
			# number of mines adjacent to the block, then those unknowns must 
			# be mines, so all we can do is register those blocks as mines
			if len(unknowns) == abs(label):
				for x,y in unknowns:
					if self.board[x][y] != 8:
						self.mse.right_click(x,y)
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
				elif self.board[xf][yf] == 8:
					mines.append((xf,yf))
					unknowns.append((xf,yf))
			# if the number of known mines is equal to the label of the block, 
			# then any unknowns adjacent to the mine must be safe, so click them
			if len(mines) == abs(label):
				for xu,yu in unknowns:
					if not (xu,yu) in self.safe_queue and not (xu,yu) in mines:
						self.safe_queue.append((xu,yu))
			else:
				self.check_queue.append((x,y))

	def do_clicks(self):
		if self.safe_queue == []:
			return False
		for x,y in self.safe_queue:
			self.mse.left_click(x,y)
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
		time.sleep(0.068)
		board_img = self.vis.screen_grab().load()
		self.profile(mid_x, mid_y, board_img)
		#self.print_board()
		self.mark_mines()
		self.determine_safes()
		while self.do_clicks():
			time.sleep(0.09)
			board_img = self.vis.screen_grab().load()
			while self.safe_queue != []:
				x,y = self.safe_queue.pop()
				self.profile(x,y,board_img)
			self.mark_mines()
			self.determine_safes()
		if self._mine_count == 40:
			print "We won!"
			PK().tap_key('Return')
			self._win_count += 1
			self._total += 1
			print self._win_count, "wins of",self._total,"games"
			self.run(self._win_count,self._total)
		else:
			print "Nope!"
			self._total += 1
			print self._win_count, "wins of",self._total,"games"
			self.run(self._win_count,self._total)
		#self.print_board()

	def run(self,wins,totals):
		print "Kicked!"
		self._vis = Vision()
		self._mine_count = 0
		self._win_count = wins
		self._total = totals
		self._mse = Mouse(self._vis)
		self._check_queue = []
		self._safe_queue = []
		self._revisit_queue = []
		(self._board,size) = self._vis.init_grid()
		self._addtups = lambda xs,ys: tuple(x+y for x,y in izip(xs,ys))
		self._surround = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
		print " > Grid identified of dimensions", size 
		self.kickoff()
