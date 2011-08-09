try:
	import pygtk
	pygtk.require("2.0")
	import gtk
	import gtk.glade
	import os
	import threading
	import gobject
except Exception, detail:
	print detail
from DialerMonitor import monitor
from Progress import ProgressDialog
from subprocess import Popen, PIPE
from Status import *
from DevicesController import DeviceController
from Screen import Screen

class operator:
	
	def __init__(self):
		self.__attrib={}
		self.__attrib["name"]=""
		self.__attrib["phone"]=""
		self.__attrib["username"]=""
		self.__attrib["password"]=""
		self.__attrib["logo"]=""
		self.__attrib["stupid_mode"]=""
	
	def add(self,atr,data):
		self.__attrib[atr]=data
	
	def get_attrib(self,atr):
		return self.__attrib[atr]

class MainInterface:
	
	def __init__(self):
		self.glade = '../data/glade/interface.glade'
		self.wTree = gtk.glade.XML(self.glade,'mainUI')
		self.window = self.wTree.get_widget('mainUI')
		#Instances
		self.__dialog = ProgressDialog()
		self.controller = DeviceController()
		self.operators = []
		self.mon = monitor()
		self.myScreen = Screen()
		
		if(self.controller.device_active != None):
			self.wTree.get_widget('label_status').set_markup("Dispositivo activo: "+self.controller.device_active.name)
			
		
		self.build_list_operators()
		self.build_combo_operators()
		self.build_sms_options()
		self.__create_graphics_cairo()
		
		#signals
		self.window.connect("destroy", self.quit_cb)
		self.__dialog.button.connect("clicked",self.cancel_connection,self.__dialog)
		self.wTree.get_widget("connect").connect("pressed",self.connect)
		self.wTree.get_widget("menu_item_about").connect("activate",self.show_about)
		self.controller.connect('added_device',self.__plug)
		self.controller.connect('removed_device',self.__unplug)
		self.mon.connect('connecting',self.__connecting_dialog)
		self.mon.connect('connected',self.__connected_dialog)
		self.mon.connect('disconnecting',self.__disconnecting_dialog)
		self.mon.connect('disconnected',self.__disconnected_dialog)
		self.mon.connect('connecting_state_change',self.__connecting_dialog)
		self.mon.connect('pppstats_signal',self.__ppp_stats)
		
		self.window.show_all()

	def build_sms_options(self):
		box_operators=self.wTree.get_widget('treeview-list')
		liststore = gtk.ListStore(gtk.gdk.Pixbuf,str)
		tvcolumn = gtk.TreeViewColumn()
		box_operators.append_column(tvcolumn)
		px = gtk.CellRendererPixbuf() 
		cell = gtk.CellRendererText()
		tvcolumn.pack_start(px, False)
		tvcolumn.pack_start(cell, True)
		tvcolumn.add_attribute(px, 'pixbuf', 0)
		tvcolumn.add_attribute(cell, 'text', 1) 
		options = ['Nuevo','Buzon de entrada','Buzon de salida','Agenda']
		icons = ['new_sms','received_sms','mail-copy','addressbook']
		i = 0
		while( i <len(options)):
			iter = liststore.append()
			liststore.set_value(iter, 1, options[i])
			logo_path ="../data/icons/"+icons[i]+ '.png'
			if os.path.exists(logo_path):
				liststore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file(logo_path))
			i = i +1
		box_operators.set_model(liststore) 
		
		box = self.wTree.get_widget('treeview')
		liststore2 = gtk.ListStore(str,str)
		cell1 = gtk.CellRendererText()
		cell2 = gtk.CellRendererText()
		tcolumn = gtk.TreeViewColumn('Numero')
		tcolumn1 = gtk.TreeViewColumn('Nombre')
		box.append_column(tcolumn)
		box.append_column(tcolumn1)
		tcolumn.pack_start(cell, True)
		tcolumn1.pack_start(cell, True)
		box.set_model(liststore2)

	def __ppp_stats(self,monitor,received,sent,interval):
		self.myScreen.update_points(received,sent)
		print str(received)+" "+str(sent)
		if (self.wTree.get_widget('notebook1').get_current_page() == 1):
			self.myScreen.update()

	def __create_graphics_cairo(self):
		kids = self.wTree.get_widget('vbox_cairo').get_children()
		if(kids is not None):
			for sprog in kids:
				self.wTree.get_widget("vbox_cairo").remove(sprog)
		self.wTree.get_widget("vbox_cairo").add(self.myScreen)
		self.wTree.get_widget("vbox_cairo").show_all()

	def __connecting_dialog(self,monitor,data = None):
		if(data == None):
			self.__dialog.label.set_markup("Conectando...")
		else:
			self.__dialog.label.set_markup(data)

	def __connected_dialog(self,monitor):
		self.__dialog.hide()
		self.wTree.get_widget("connect").set_label("Desconectar")
		self.wTree.get_widget("connect").set_active(True)
		self.window.set_sensitive(True)

	def __disconnecting_dialog(self,monitor):
		self.__dialog.label.set_markup("Desconectando...")

	def __disconnected_dialog(self,monitor):
		self.__dialog.should_change = False
		self.__dialog.image.set_from_file('../data/icons/network-error.png')
		self.__dialog.label.set_markup("Error")
		self.__dialog.button.set_label("Cerrar")

	def __plug(self,m_controller,dev):
		self.wTree.get_widget('label_status').set_markup("Dispositivo activo: "+dev)

	def __unplug(self,m_controller):
		self.wTree.get_widget('label_status').set_markup('No hay ningun dispositivo activo')

	def build_list_operators(self):
		from xml.dom.minidom import parse
		
		midom = parse('../data/conf/operators.xml')
		m_operators = midom.childNodes[0].childNodes
		for m_operator in m_operators:
			if (m_operator.nodeType == 1):
				op = operator()
				op.add("name",m_operator.attributes.get("name").value)
				attribs = m_operator.childNodes
				for attrib in attribs:
					if(attrib.nodeType == 1):
						op.add(attrib.nodeName,attrib.childNodes[0].data)
				self.operators.append(op)

	def connect(self,widget, data = None):
		if (self.mon.status() == PPP_STATUS_DISCONNECTED):
			combo = self.wTree.get_widget('combobox')
			active = combo.get_active()
			self.window.set_sensitive(False)
			self.__dialog.show()
			self.mon.start(self.operators[active],self.controller.device_active.port['data'])
		else:
			widget.set_label("Conectar")
			self.mon.stop()

	def cancel_connection(self,widget,dialog,data = None):
		if(self.mon.status() == PPP_STATUS_CONNECTING):
			self.mon.stop()
			return
		if(self.mon.status() == PPP_STATUS_DISCONNECTED):
			dialog.hide()
			self.window.set_sensitive(True)

	def show_about(self,widget):
		self.about = gtk.glade.XML(self.glade,'about-dialog')
		self.about.get_widget('about-dialog').show_all()

	def build_combo_operators(self):
		box_operators=self.wTree.get_widget('combobox')
		liststore = gtk.ListStore(gtk.gdk.Pixbuf,str)
		px = gtk.CellRendererPixbuf() 
		cell = gtk.CellRendererText()
		box_operators.pack_start(px)
		box_operators.pack_start(cell)
		box_operators.add_attribute(px, 'pixbuf', 0)
		box_operators.add_attribute(cell, 'text', 1) 
		for i in self.operators:
			iter = liststore.append()
			liststore.set_value(iter, 1, i.get_attrib('name'))
			logo_path ="../data/icons/"+i.get_attrib('logo')+ '.png'
			if os.path.exists(logo_path):
				liststore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file(logo_path))
		box_operators.set_model(liststore)
		box_operators.set_active(-1)

	def quit_cb(self,widget, data=None):
		gtk.main_quit()

def main():
	gtk.main()

if __name__ == "__main__":
	m_interface = MainInterface()
	main()
