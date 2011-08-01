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
from dialerMonitor import monitor
from progress import ProgressDialog
from subprocess import Popen, PIPE
from status import *

class MainInterface:
	
	def __init__(self):
		self.wTree = gtk.glade.XML('interface2.glade','mainUI')
		self.window = self.wTree.get_widget('mainUI')
		self.__dialog = ProgressDialog()
		self.__dialog.button.connect("clicked",self.cancel_connection,self.__dialog)
		self.operators = range(3)
		self.avalaible_devices = range(2)
		self.mon = monitor()
		self.device_active = None
		self.build_list_operators()
		self.build_combo_operators()
		self.window.connect("destroy", self.quit_cb)
		self.wTree.get_widget("connect").connect("pressed",self.connect)
		self.wTree.get_widget("menu_item_about").connect("activate",self.show_about)
		self.__build_avalaible_devices()
		self.__hardware_detection()
		self.window.show_all()
	
	def build_list_operators(self):
		file = open("operators","r")
		i=0
		for line in file:
			line = line.strip()
			if(line=="<operator>"):
				self.operators[i]=operator()
				for line in file:
					line = line.strip()
					if(line=="</operator>"):
						break
					else:
						split=line.split("=")
						self.operators[i].add(split[0],split[1])
				i=i+1
		file.close()

	def connect(self,widget, data = None):
		if (self.mon.status() == PPP_STATUS_DISCONNECTED):
			combo = self.wTree.get_widget('combobox')
			active = combo.get_active()
			self.window.set_sensitive(False)
			self.__dialog.show()
			self.mon.start(self.operators[active],self.device_active.get_attrib("nodo"))
			gobject.timeout_add_seconds(1,self.checking_connection)
		else:
			widget.set_label("Conectar")
			self.mon.stop()

	def checking_connection(self):
		if(self.mon.status() == PPP_STATUS_CONNECTING):
			self.__dialog.label.set_markup(self.mon.get_state())
			return True
		elif (self.mon.status() == PPP_STATUS_CONNECTED):
			self.__dialog.hide()
			self.wTree.get_widget("connect").set_label("Desconectar")
			self.wTree.get_widget("connect").set_active(True)
			self.window.set_sensitive(True)
			return False
		else:
			self.__dialog.should_change = False
			self.__dialog.image.set_from_file('network-error.png')
			self.__dialog.label.set_markup("Error")
			return False

	def cancel_connection(self,widget,dialog,data = None):
		if(self.mon.status() == PPP_STATUS_CONNECTING):
			self.mon.stop()
		dialog.hide()
		self.window.set_sensitive(True)

	def show_about(self,widget):
		self.about = gtk.glade.XML('interface2.glade','about-dialog')
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
			logo_path =i.get_attrib('logo')+ '.png'
			if os.path.exists(logo_path):
				liststore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file(logo_path))
		box_operators.set_model(liststore)
		box_operators.set_active(-1)

	def __hardware_detection(self):
		cmd = "lsusb"
		pm =  Popen(cmd, shell=True, stdout=PIPE, close_fds=True)
		for line in pm.stdout:
			line = line.split(" ")[5]
			vendor, product = line.split(":")
			if(vendor!="1d6b"):
				for iter in self.avalaible_devices:
					if(vendor == iter.get_attrib("idVendor") and product == iter.get_attrib("idProduct")):
						self.device_active=iter
						break
				if(self.device_active!=None):
					break

	def __build_avalaible_devices(self):
		file = open("modems.xml","r")
		i=0
		for line in file:
			line = line.strip()
			line = line.split(" ")
			if(len(line) > 1):
				if(line[0]=="<product"):
					sp = line[1].split("=")
					vendor, product = sp[1].split(":")
					self.avalaible_devices[i] = modem(vendor,product)
					iter = 2
					while(iter<len(line)-1):
						split = line[iter].split("=")
						self.avalaible_devices[i].add(split[0],split[1])
						iter = iter + 1
					i = i+1

	def quit_cb(self,widget, data=None):
		gtk.main_quit()

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

class modem:
	def __init__(self, idVendor=None, idProduct=None):
		self.__attrib={}
		self.__attrib["idVendor"]=idVendor
		self.__attrib["idProduct"]=idProduct

	def add(self,atr,data):
		self.__attrib[atr]=data

	def get_attrib(self,atr):
		return self.__attrib[atr]

def main():
	gtk.main()

if __name__ == "__main__":
	m_interface = MainInterface()
	main()
