#!/usr/bin/env python


import os
import gtk
import gobject
import pyosd

class Status(gtk.StatusIcon,gobject.GObject):
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        gobject.GObject.__init__(self)
        menu = '''
            <ui>
             <menubar name="Menubar">
              <menu action="Menu">
               <menuitem action="View"/>
               <menuitem action="About"/>
               <separator/>
               <menuitem action="Quit"/>
              </menu>
             </menubar>
            </ui>
        '''
        actions = [
            ('Menu',  None, 'Menu'),
            ('View', None, '_Mostrar ventana', None, 'Mostrar ventana', self.on_activate),
            ('About', gtk.STOCK_ABOUT, '_Acerca de Nugget', None, 'Acerca de Nugget', self.on_about),
            ('Quit',None,'_Salir',None,None,self.on_quit)]
        ag = gtk.ActionGroup('Actions')
        ag.add_actions(actions)
        self.manager = gtk.UIManager()
        self.manager.insert_action_group(ag, 0)
        self.manager.add_ui_from_string(menu)
        self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent
        self.set_from_stock(gtk.STOCK_FIND)
        self.set_tooltip('Tracker Desktop Search')
        self.set_visible(True)
        self.connect('activate', self.on_activate)
        self.connect('popup-menu', self.on_popup_menu)

    def on_activate(self, data):
        #os.spawnlpe(os.P_NOWAIT, 'tracker-search-tool', os.environ)
        print 'search'
        osd = pyosd.osd()
        #osd.set_colour("red")
        #osd.set_align(pyosd.ALIGN_CENTER)
        osd.display('hola')
        osd.wait_until_no_display()
        #osd.show()

    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, None, button, time)

    def on_preferences(self, data):
        print 'preferences'

    def on_about(self, data):
        dialog = gtk.AboutDialog()
        dialog.set_name('Tracker')
        dialog.set_version('0.5.0')
        dialog.set_comments('A desktop indexing and search tool')
        dialog.set_website('www.freedesktop.org/Tracker')
        dialog.run()
        dialog.destroy()

    def on_quit(self,data):
        print 'quit'
        gtk.main_quit()

if __name__ == '__main__':
    Status()
    gtk.main()