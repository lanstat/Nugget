#coding:utf-8

import pygtk
pygtk.require20()
import gtk

from uadh import gui
from uadh.gui import gtk2gui

from uadh.plugins import Plugin
import mobile

class Main(Plugin):
    def __init__(self, data):
        Plugin.__init__(self, data)
        self._view = data.view

    def run(self):
        s = gui.Section('Monitor',MonitorGui(self._view))
        self._view.add_section(s)

    def get_id(self):
        return 'monitor-plugin'

class MonitorGui(gtk.Table):
    def __init__(self, view):
        gtk.Table.__init__(self, rows = 5, columns = 1)
        self._mainView = view
        self.attach(NetHistoryGui(),0,1,0,1, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)

class NetHistoryGui(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self)
        lbl = gtk.Label()
        lbl.set_markup('<b>Histórico de la red</b>')
        self.set_shadow_type(gtk.SHADOW_NONE)
        self.set_label_widget(lbl)
        table = gtk.Table(rows = 3, columns = 3)
        self.add(table)