try:
	import pygtk
	pygtk.require("2.0")
	import gtk
	import gobject
except Exception, detail:
	print detail
	
class ProgressDialog:
	
	def __init__(self):
		self.glade = 'interface2.glade'
		self.dTree = gtk.glade.XML(self.glade, 'progress_dialog')
		self.window = self.dTree.get_widget('progress_dialog')
		self.label = self.dTree.get_widget('label_operation')
		self.button = self.dTree.get_widget('button_cancel')
		self.image = self.dTree.get_widget('image2')
		self.should_change = True
		self.__switch = True

	def show(self):
		def image_change():
			if(not self.should_change):
				return False
			if(self.__switch):
				self.image.set_from_file('network-transmit.png')
				self.__switch = False
			else:
				self.image.set_from_file('network-receive.png')
				self.__switch = True
			return self.should_change
		self.should_change = True
		self.window.show_all()
		gobject.timeout_add_seconds(1, image_change)

	def hide(self):
		self.__should_change = False
		self.window.hide()	
