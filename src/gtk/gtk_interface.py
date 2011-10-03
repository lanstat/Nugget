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

import sys
sys.path.append('/home/lance/aplicaciones/nugget/src/core')
from DialerMonitor import monitor
from Progress import ProgressDialog
from subprocess import Popen, PIPE
from Status import *
from DevicesController import DeviceController
from Screen import Screen
from DeviceSerial import PhoneData
from const import *
from util import operator
from interface import Interface
import osd

class MainInterface:
	
	def __init__(self):
		#Instances
		self.__interface = Interface()
		self.__dialog = ProgressDialog()
		self.controller = DeviceController()
		self.dev_active = self.controller.device_active
		self.operators = []
		self.mon = monitor()
		self.myScreen = Screen()
		self.phone_data = None
		
		self.build_list_operators()
		self.build_combo_operators()
		self.build_phone_options()
		self.__create_graphics_cairo()
		self.__create_sms_model()
		self.__create_address_book_model()
		
		if(self.dev_active != None):
			self.__interface.set_status("Dispositivo activo: "+self.dev_active.name)
			gobject.timeout_add_seconds(5,self.__connect_to_phone)
		
		#vars
		self.__last_received = 0
		self.__last_sent = 0
		
		#signals
		self.__dialog.button.connect("clicked",self.cancel_connection,self.__dialog)
		self.__interface.window.connect("destroy", self.quit_cb)
		self.__interface.button_connect.connect("pressed",self.connect)
		self.__interface.menu_about.connect("activate",self.show_about)
		self.__interface.box_options.connect("cursor-changed",self.change_option)
		self.__interface.send_sms.connect('clicked',self.send_message)
		self.controller.connect('added_device',self.__plug)
		self.controller.connect('removed_device',self.__unplug)
		
		#self.__interface.button1.connect("pressed",self.__connect_to_phone)
		
		self.mon.connect('connecting',self.__connecting_dialog)
		self.mon.connect('connected',self.__connected_dialog)
		self.mon.connect('disconnecting',self.__disconnecting_dialog)
		self.mon.connect('disconnected',self.__disconnected_dialog)
		self.mon.connect('connecting_state_change',self.__connecting_dialog)
		self.mon.connect('pppstats_signal',self.__ppp_stats)
		
		self.__interface.window.show_all()

	def __show_signal(self,phonedata,signal):
		if(self.phone_data != None):
			#signal = int(self.phone_data.get_signal())
			if(signal>=23):
				path = ICONS_DIR+'nm-signal-100.png'
			elif(signal>=15):
				path = ICONS_DIR+'nm-signal-75.png'
			elif(signal>=8):
				path = ICONS_DIR+'nm-signal-25.png'
			else:
				path = ICONS_DIR+'nm-signal-00.png'
		else:
			path = ICONS_DIR+'nm-signal-00.png'
		self.__interface.image_signal.set_from_file(path)

	def build_phone_options(self):
		box_options=self.__interface.box_options
		liststore = gtk.ListStore(gtk.gdk.Pixbuf,str)
		tvcolumn = gtk.TreeViewColumn()
		box_options.append_column(tvcolumn)
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
			logo_path =ICONS_DIR + icons[i]+ '.png'
			if os.path.exists(logo_path):
				liststore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file(logo_path))
			i = i +1
		box_options.set_model(liststore) 

	def __create_address_book_model(self):
		box = self.__interface.box_address
		cell1 = gtk.CellRendererText()
		cell2 = gtk.CellRendererText()
		tcolumn = gtk.TreeViewColumn('Nombre')
		tcolumn1 = gtk.TreeViewColumn('Numero')
		box.append_column(tcolumn)
		box.append_column(tcolumn1)
		tcolumn.pack_start(cell1, True)
		tcolumn1.pack_start(cell2, True)
		tcolumn.add_attribute(cell1, 'text',0)
		tcolumn1.add_attribute(cell2, 'text',1)

	def __create_address_book_list(self):
		liststore2 = gtk.ListStore(str,str)
		list = self.phone_data.get_addressbook()
		for item in list:
			if(item != None):
				iter = liststore2.append()
				liststore2.set_value(iter,0,item.get_name())
				liststore2.set_value(iter,1,item.get_phone_number())
			else:
				break
		self.__interface.box_address.set_model(liststore2)

	def __create_sms_model(self):
		box = self.__interface.box_sms
		cell1 = gtk.CellRendererText()
		cell2 = gtk.CellRendererText()
		cell3 = gtk.CellRendererText()
		tcolumn = gtk.TreeViewColumn('Numero')
		tcolumn1 = gtk.TreeViewColumn('Asunto')
		tcolumn2 = gtk.TreeViewColumn('Fecha')
		box.append_column(tcolumn)
		box.append_column(tcolumn1)
		box.append_column(tcolumn2)
		tcolumn.pack_start(cell1, True)
		tcolumn1.pack_start(cell2, True)
		tcolumn2.pack_start(cell3, True)
		tcolumn.add_attribute(cell1, 'text',0)
		tcolumn1.add_attribute(cell2, 'text',1)
		tcolumn2.add_attribute(cell3, 'text',2)

	def __create_sms_list(self):
		list = self.phone_data.get_old_sms()
		liststore2 = gtk.ListStore(str,str,str)
		for item in list:
			if(item <> None):
				iter = liststore2.append()
				liststore2.set_value(iter,0,item.get_phone_number())
				liststore2.set_value(iter,1,item.get_message())
				liststore2.set_value(iter,2,item.get_date())
		self.__interface.box_sms.set_model(liststore2)

	def __add_sms_list(self, phonedata):
		list = self.phone_data.get_new_sms()
		liststore2 = self.__interface.box_sms.get_model()
		for sms in list:
			if(sms <> None):
				iter = liststore2.preppend()
				liststore2.set_value(iter,0,item.get_phone_number())
				liststore2.set_value(iter,1,item.get_message())
				liststore2.set_value(iter,2,item.get_date())
		self.__interface.box_sms.set_model(liststore2)

	def __ppp_stats(self,monitor,received,sent,interval):
		up_speed = ((sent - self.__last_sent)/interval)/1024
		down_speed = ((received - self.__last_received)/interval)/1024
		self.__last_sent = sent
		self.__last_received = received
		self.myScreen.update_points(down_speed,up_speed)
		if (self.__interface.notebook.get_current_page() == 1):
			self.__interface.upspeed.set_markup(str(up_speed)+" KB")
			self.__interface.downspeed.set_markup(str(down_speed)+" KB")
			self.__interface.label_up.set_markup(str(sent)+" KB")
			self.__interface.label_down.set_markup(str(received)+" KB")
			
			self.myScreen.update()

	def __create_graphics_cairo(self):
		kids = self.__interface.vbox_cairo.get_children()
		if(kids is not None):
			for sprog in kids:
				self.__interface.vbox_cairo.remove(sprog)
		self.__interface.vbox_cairo.add(self.myScreen)
		self.__interface.vbox_cairo.show_all()

	def __connecting_dialog(self,monitor,data = None):
		if(data == None):
			self.__dialog.change_message("Conectando...")
		else:
			self.__dialog.change_message(data)

	def __connected_dialog(self,monitor,ip):
		self.__dialog.hide()
		self.__interface.label_ip.set_markup(ip)
		self.__interface.button_connect.set_label("Desconectar")
		self.__interface.button_connect.set_active(True)
		self.__interface.window.set_sensitive(True)
		osd.show_connected(ip,'10.23.4.5')

	def __disconnecting_dialog(self,monitor):
		self.__dialog.show_disconnect("Desconectando...")

	def __disconnected_dialog(self,monitor):
		self.__dialog.should_change = False
		self.__dialog.show_disconnect('Correctamente desconectado.')
		self.__dialog.hide()
		self.__interface.window.set_sensitive(True)
		osd.show_disconnect()

	def __plug(self,m_controller,dev):
		self.dev_active = self.controller.device_active
		self.__interface.set_status("Dispositivo activo: "+dev)
		gobject.timeout_add_seconds(15,self.__connect_to_phone)
		osd.show_device_found(dev)

	def __connect_to_phone(self):
		self.phone_data = PhoneData(self.dev_active.port['conf'])
		signal = self.phone_data.get_signal()
		self.__show_signal(self.phone_data,signal)
		self.phone_data.connect('signal_update',self.__show_signal)
		self.phone_data.connect('new_sms',self.__add_sms_list)
		self.__create_sms_list()
		self.__create_address_book_list()
		
		return False

	def __unplug(self,m_controller):
		self.__interface.set_status('No hay ningun dispositivo activo')
		self.phone_data = None

	def build_list_operators(self):
		from xml.dom.minidom import parse
		
		midom = parse(CONF_DIR + 'operators.xml')
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
		if(self.controller.device_active == None):
			self.__dialog.show_error("No hay dispositivo conectado.")
			return
		combo = self.__interface.combo_operator
		active = combo.get_active()
		if(active == -1):
			self.__dialog.show_error('Seleccione un operador.')
			return
		if(self.mon.status() == PPP_STATUS_DISCONNECTED):
			self.__interface.window.set_sensitive(False)
			self.__dialog.show()
			self.mon.start(self.operators[active],self.dev_active.port['data'])
		else:
			widget.set_label("Conectar")
			self.mon.stop()

	def send_message(self,widget):
		if(self.phone_data <> None):
			phone,message = self.__interface.send_message()
			self.phone_data.send_sms(message,phone)
		else:
			self.__dialog.show_phone_error('No hay un dispositivo conectado.')

	def cancel_connection(self,widget,dialog,data = None):
		if(self.mon.status() == PPP_STATUS_CONNECTING):
			self.mon.stop()
			return
		if(self.mon.status() == PPP_STATUS_DISCONNECTED):
			dialog.hide()
			self.__interface.window.set_sensitive(True)

	def show_about(self,widget):
		self.__interface.show_about()

	def change_option(self,widget):
		treeselection = widget.get_selection()
		(model, iter) = treeselection.get_selected()
		[path,] = model.get_path(iter)
		self.__interface.notebook_phone.set_current_page(path)

	def build_combo_operators(self):
		box_operators=self.__interface.combo_operator
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
			logo_path =ICONS_DIR+i.get_attrib('logo')+ '.png'
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
