import pyscreenshot as PSS
from pymouse import PyMouse as PM

class OSIMS:
    
	@property
	def border(self):
		return self._border

	@property
	def size(self):
		return self._size

	"""Right now, all I will do is mandate the size of the grid. In the future,
	we will automate size initialization.
	args: img is an Image object.
	returns: the 2D array that represents a new Minesweeper grid. """
	@staticmethod
	def _id_size(img):
		x = 16
		y = 16
		return [[0 for i in range(x)] for i in range(y)],x,y

	def kickoff(self):
		x, y = self.size
		lef, top = self.border
		mid_x = x/2
		mid_y = y/2
		PM().click(lef + (mid_x * 16 - 8), top + (mid_y * 16 - 8),1)

	def run(self):
		h = 256
		w = 256
		lef = 428
		top = 255
		rgt = lef + w
		bot = top + h
		self._border = (lef,top)
		self._init_coord = (lef,top,rgt,bot)
		self._vis_mem_loc = "vis_mem.png"
		print "Kicked!"
		focus = PSS.grab(self._init_coord)
		focus.save(self._vis_mem_loc)
		print " > Image Aquired at", self._vis_mem_loc
		grid,hght,wdth = self._id_size(focus)
		self._size = hght,wdth
		print " > Grid identified of dimensions", self._size 
		self.kickoff()
