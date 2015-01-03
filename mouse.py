from pymouse import PyMouse as PM
import time

class Mouse:

	@property
	def vis(self):
		return self._vis

	def __init__(self,vis):
		self._vis = vis
		self.pm = PM()

	""" Takes a board coordinate (x,y) and uses self._vis to calculate the
	screen coordinates to click there. Then it waits 5.7 ms, and takes a 
	screenshot"""
	def left_click(self,x,y):
		#print "clicking at",x,y
		x0, y0 = self.vis.edge_coords
		x1, y1 = (x0 + 8 + x * 16, y0 + 8 + y * 16)
		self.pm.move(x1,y1)
		self.pm.click(x1,y1,1)
		#time.sleep(0.068)
	
	def right_click(self,x,y):
		x0, y0 = self.vis.edge_coords
		x1, y1 = (x0 + 8 + x * 16, y0 + 8 + y * 16)
		self.pm.click(x1,y1,2)
		#time.sleep(0.068)

	""" Uses self._vis to determine the position of the smiley reset button"""
	def reset_board(self):
		(resx, resy) = self.vis.get_reset()
		self.pm.move(resx,resy)
		self.pm.press(resx,resy,1)
		time.sleep(0.5)
		self.pm.release(resx,resy,1)
