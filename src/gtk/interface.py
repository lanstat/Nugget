try:
	import pygtk
	pygtk.require("2.0")
	import gtk
	import gtk.glade
except Exception, detail:
	print detail
from const import *


class Interface:
	
	def __init__(self):
		self.glade = GLADE_DIR + 'interface.glade'
		self.wTree = gtk.glade.XML(self.glade,'mainUI')
		self.window = self.wTree.get_widget('mainUI')
		self.label_status = self.wTree.get_widget('label_status')
		self.image_signal = self.wTree.get_widget('image1')
		self.box_options = self.wTree.get_widget('treeview-list')
		self.box_address = self.wTree.get_widget('treeview-address')
		self.box_sms = self.wTree.get_widget('treeview_sms')
		self.notebook = self.wTree.get_widget('notebook1')
		self.upspeed = self.wTree.get_widget('upspeed')
		self.downspeed = self.wTree.get_widget('downspeed')
		self.label_up = self.wTree.get_widget('uplabel')
		self.label_down = self.wTree.get_widget('downlabel')
		self.label_ip = self.wTree.get_widget("iplabel")
		self.button_connect = self.wTree.get_widget("connect")
		self.combo_operator = self.wTree.get_widget('combobox')
		self.menu_about = self.wTree.get_widget('menu_item_about')
		self.vbox_cairo = self.wTree.get_widget('vbox_cairo')
		self.button1 = self.wTree.get_widget("button1")
		self.send_sms = self.wTree.get_widget('send_sms')
		self.notebook_phone = self.wTree.get_widget('nb_phone')

	def set_status(self, msg):
		self.label_status.set_markup(msg)

	def show_about(self):
		self.about = gtk.glade.XML(self.glade,'about-dialog')
		self.about.get_widget('about-dialog').show_all()

	def send_message(self):
		phone = self.wTree.get_widget('entry_phone').get_text()
		buffer = self.wTree.get_widget('tv_sms').get_buffer()
		start, end = buffer.get_bounds()
		message = buffer.get_text(start, end, include_hidden_chars=True)
		return (phone,message)


