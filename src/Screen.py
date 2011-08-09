import gtk
import gtk.glade
import cairo
import gobject
from random import random

class Point:
	def __init__(self, p_x = 0, p_y = 0):
		self.down = p_x
		self.up = p_y

class Screen(gtk.DrawingArea):
	def __init__(self):
		super(Screen, self).__init__()
		self.intervals = []
		self.set_size_request(200,200)
		self.connect("expose_event", self.expose)
		self.update()

	def redraw_canvas(self):
		if self.window:
			alloc = self.get_allocation()
			rect = gtk.gdk.Rectangle(alloc.x, alloc.y, alloc.width, alloc.height)
			self.window.invalidate_rect(rect, True)
			self.queue_draw_area(alloc.x, alloc.y, alloc.width, alloc.height)
			self.window.process_updates(True)

	def update(self):
		self.redraw_canvas()
		return True

	def expose(self,widget,event):
		context = widget.window.cairo_create()
		context.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		context.clip()
		rect = self.get_allocation()
		print str(rect.width)+" "+str(rect.height)
		self.draw(context,rect.width,rect.height)
		return False

	def draw(self, cr, width, height):
		self.style.apply_default_background(self.window, True, gtk.STATE_NORMAL, None, 0, 0, width, height)
		cr.set_source_rgb( 0, 0, 0)
		cr.rectangle(0, 0, width, height)
		cr.fill()
		if(len(self.intervals) > 0):
			position = self.intervals[0]
			pos_x=200-len(self.intervals)*5
		for point in self.intervals:
			cr.set_source_rgb( 1, 0, 0)
			cr.move_to(pos_x,position.down)
			pos_x = pos_x+5
			cr.line_to(pos_x,point.down)
			position = point
		cr.set_line_width(1.5)
		cr.stroke()
		if(len(self.intervals) > 0):
			position = self.intervals[0]
			pos_x=200-len(self.intervals)*5
		for point in self.intervals:
			cr.set_source_rgb( 0, 0, 1)
			cr.move_to(pos_x,position.up)
			pos_x = pos_x+5
			cr.line_to(pos_x,point.up)
			position = point
		cr.set_line_width(1.5)
		cr.stroke()

	def update_points(self,down,up):
		if(len(self.intervals) == 40):
			del self.intervals[0]
		self.intervals.append(Point(down,up))
		#print str(down)+" "+str(up)
