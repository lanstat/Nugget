import pygtk
pygtk.require20()
import gtk
from gtk import glade

from uadh import gui
from uadh.gui import gtk2gui
from uadh.plugins import Plugin

class Main(Plugin):
    def __init__(self, data):
        Plugin.__init__(self, data)
        self._view = data.view

    def run(self):
        s = gui.Section('WebSms',WebSms(self._data))
        self._view.add_section(s)

    def get_id(self):
        return 'websms-plugin'

class WebSms(gtk.Table):
    def __init__(self, view):
        gtk.Table.__init__(self, rows = 5, columns = 1)
