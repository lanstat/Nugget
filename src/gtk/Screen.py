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
		self.__intervals = []
		self.__limite = 36
		self.__width = 0
		self.__height = 0
		self.__max_speed = 100
		self.connect("expose_event", self.expose)
		self.update()

	def redraw_canvas(self):
		if self.window:
			alloc = self.get_allocation()
			rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
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
		self.__limite = int((rect.width-30)/5)
		self.__width = rect.width
		self.__height = rect.height
		self.draw(context,rect.width,rect.height)
		return False

	def draw(self, cr, width, height):
		self.style.apply_default_background(self.window, True, gtk.STATE_NORMAL, None, 0, 0, width, height)
		cr.set_source_rgb( 0, 0, 0)
		cr.rectangle(0, 0, width, height)
		cr.fill()
		if(len(self.__intervals) > 0):
			position = self.__intervals[0]
			pos_x=width-len(self.__intervals)*5
		cr.set_source_rgb( 1, 0, 0)
		for point in self.__intervals:
			cr.move_to(pos_x,position.down)
			pos_x = pos_x+5
			cr.line_to(pos_x,point.down)
			position = point
		cr.set_line_width(1.5)
		cr.stroke()
		if(len(self.__intervals) > 0):
			position = self.__intervals[0]
			pos_x=width-len(self.__intervals)*5
		cr.set_source_rgb( 0, 0, 1)
		for point in self.__intervals:
			cr.move_to(pos_x,position.up)
			pos_x = pos_x+5
			cr.line_to(pos_x,point.up)
			position = point
		cr.set_line_width(1.5)
		cr.stroke()
		self.__draw_frame(cr,width, height)

	def __draw_frame(self, cr, width, height):
		cr.set_source_rgb( 1, 1, 1)
		cr.move_to(40,10)
		cr.line_to(40,height-20)
		cr.move_to(40,height-20)
		cr.line_to(width-10,height-20)
		cr.set_line_width(1.5)
		cr.stroke()
		cr.move_to(10,10)
		cr.select_font_face("Droid")
		cr.set_font_size(12)
		cr.show_text(str(self.__max_speed))
		cr.move_to(450,15)
		cr.set_source_rgb(1,0,0)
		cr.show_text("Datos Recibidos")
		cr.move_to(450,30)
		cr.set_source_rgb(0,0,1)
		cr.show_text("Datos Enviados")

	def update_points(self,down,up):
		if(len(self.__intervals) == self.__limite):
			del self.__intervals[0]
		if(down>self.__max_speed):
			while(down>self.__max_speed):
				self.__max_speed = self.__max_speed + 50
		down = (156*down)/self.__max_speed
		up = (156*up)/self.__max_speed
		down = self.__height - 30 - down
		up = self.__height - 30 - up
		self.__intervals.append(Point(down,up))
