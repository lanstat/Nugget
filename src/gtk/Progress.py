try:
	import pygtk
	pygtk.require("2.0")
	import gtk
	import gobject
except Exception, detail:
	print detail

import sys
sys.path.append('/home/lance/aplicaciones/nugget/src/core')
from const import GLADE_DIR, ICONS_DIR


class ProgressDialog:
	
	def __init__(self):
		self.glade = GLADE_DIR + 'interface.glade'
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
				self.image.set_from_file(ICONS_DIR + 'network-transmit.png')
				self.__switch = False
			else:
				self.image.set_from_file(ICONS_DIR + 'network-receive.png')
				self.__switch = True
			return self.should_change
		self.should_change = True
		self.window.show_all()
		gobject.timeout_add_seconds(1, image_change)

	def show_error(self, msg):
		self.image.set_from_file(ICONS_DIR + 'network-error.png')
		self.label.set_markup(msg)
		self.button.set_label('Cerrar')
		self.window.show_all()

	def show_disconnect(self,msg):
		self.image.set_from_file(ICONS_DIR + 'network-offline.png')
		self.label.set_markup(msg)
		self.button.set_label('Cerrar')
		self.window.show_all()

	def show_phone_error(self,msg):
		self.image.set_from_file(ICONS_DIR + 'modem-warning.png')
		self.label.set_markup(msg)
		self.button.set_label('Cerrar')
		self.window.show_all()

	def change_message(self, msg):
		self.label.set_markup(msg)

	def hide(self):
		self.__should_change = False
		self.window.hide()	
