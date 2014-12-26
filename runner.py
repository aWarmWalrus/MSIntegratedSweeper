from PIL import ImageGrab as ig

class run:
	def __init__(self):
		self._init_coord = (373,92,871,408)
		self._vis_mem_loc = "vis_mem.jpg"
		print "Kicked!"
		focus = ig.grab(self._init_coord)
		focus.save(self._vis_mem_loc)
		print " > Image Aquired at", self._vis_mem_loc
		grid = _id_size(focus)

	"""Right now, all I will do is mandate the size of the grid. In the future,
	we will automate size initialization.
	args: img is an Image object.
	returns: the 2D array that represents a new Minesweeper grid. """
	def _id_size(img):


j = run()