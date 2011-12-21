#coding:utf-8

import pygtk
pygtk.require20()
import gtk, os, threading, gobject
from gtk import glade

from uadh import gui
from uadh.gui import gtk2gui
from uadh.plugins import Plugin
import mobile
from DialerMonitor import Monitor 
from Progress import ProgressDialog
from subprocess import Popen, PIPE
from Status import *
import osd

class Main(Plugin):
    def __init__(self, data):
        Plugin.__init__(self, data)
        self._view = data.view

    def run(self):
        s = gui.Section('Conectar',ConnectorGui(self._data))
        self._view.add_section(s)

    def get_id(self):
        return 'connector-plugin'

class ConnectorGui(gtk.Table):
    def __init__(self, data):
        gtk.Table.__init__(self, rows = 3, columns = 4)
        self._mainView = data.view
        self._data = data
        self.attach(gtk.Fixed(),0,4,0,1)
        self.attach(gtk.Fixed(),0,1,1,2, xpadding = 10, ypadding = 10)
        self._cmbOperators = gtk.ComboBox()
        self.attach(self._cmbOperators,1,2,1,2, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)
        self._btnConnect = gtk.ToggleButton('Conectar')
        self.attach(self._btnConnect,2,3,1,2, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)
        self.attach(gtk.Fixed(),3,4,1,2, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)
        self.attach(gtk.Fixed(),0,4,2,3)

        #Instances
        self.__dialog = ProgressDialog(self._mainView)
        self.controller = self._data.model.controller
        self.operators = []
        self.mon = Monitor()
        
        if(self.controller.device_active != None):
            self._mainView.set_status_message("Dispositivo activo: " + self.controller.device_active.name)
        
        self.build_list_operators()
        self.build_combo_operators()
        
        #signals
        self.__dialog.button.connect("clicked",self.cancel_connection,self.__dialog)
        self._btnConnect.connect("pressed",self.connect)
        self.controller.connect('added_device',self.__plug)
        self.controller.connect('removed_device',self.__unplug)
        self.mon.connect('connecting',self.__connecting_dialog)
        self.mon.connect('connected',self.__connected_dialog)
        self.mon.connect('disconnecting',self.__disconnecting_dialog)
        self.mon.connect('disconnected',self.__disconnected_dialog)
        self.mon.connect('connecting_state_change',self.__connecting_dialog)

    def __connecting_dialog(self,monitor,data = None):
        if(data == None):
            self.__dialog.set_status_message("Conectando...")
        else:
            self.__dialog.set_status_message(data)

    def __connected_dialog(self,monitor,ip):
        self.__dialog.hide()
        self._btnConnect.set_label("Desconectar")
        self._btnConnect.set_active(True)
        osd.show_connected(ip,'10.23.4.5')

    def __disconnecting_dialog(self,monitor):
        self.__dialog.set_status_message("Desconectando...")
        self.__dialog.show()

    def __disconnected_dialog(self,monitor):
        self.__dialog.should_change = False
        self.__dialog.image.set_from_file('./modules/connector/data/icons/network-error.png')
        self.__dialog.set_status_message("Error")
        self.__dialog.button.set_label("Cerrar")
        osd.show_disconnect()

    def __plug(self,m_controller,dev):
        self._mainView.set_status_message("Dispositivo activo: "+dev)

    def __unplug(self,m_controller):
        self._mainView.set_status_message('No hay ningun dispositivo activo')

    def build_list_operators(self):
        from xml.dom.minidom import parse
        midom = parse('./modules/connector/data/conf/operators.xml')
        m_operators = midom.childNodes[0].childNodes
        for m_operator in m_operators:
            if (m_operator.nodeType == 1):
                op = Operator()
                op.add("name",m_operator.attributes.get("name").value)
                attribs = m_operator.childNodes
                for attrib in attribs:
                    if(attrib.nodeType == 1):
                        op.add(attrib.nodeName,attrib.childNodes[0].data)
                self.operators.append(op)

    def connect(self,widget, data = None):
        if (self.mon.status() == PPP_STATUS_DISCONNECTED):
            active = self._cmbOperators.get_active()
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

    def build_combo_operators(self):
        liststore = gtk.ListStore(gtk.gdk.Pixbuf,str)
        px = gtk.CellRendererPixbuf() 
        cell = gtk.CellRendererText()
        self._cmbOperators.pack_start(px)
        self._cmbOperators.pack_start(cell)
        self._cmbOperators.add_attribute(px, 'pixbuf', 0)
        self._cmbOperators.add_attribute(cell, 'text', 1) 
        for i in self.operators:
            iter = liststore.append()
            liststore.set_value(iter, 1, i.get_attrib('name'))
            logo_path ="./modules/connector/data/icons/"+i.get_attrib('logo')+ '.png'
            if os.path.exists(logo_path):
                liststore.set_value(iter, 0, gtk.gdk.pixbuf_new_from_file(logo_path))
        self._cmbOperators.set_model(liststore)
        self._cmbOperators.set_active(-1)


class Operator:
    
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
