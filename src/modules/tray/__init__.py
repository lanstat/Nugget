#!/usr/bin/env python


import os
import gtk
import gobject

from uadh.plugins import Plugin
import mobile

#try:
#    import appindicator
#    sw=0
#    print "Se importa modulo appindicator"
#except:
#    sw=1
#    print "Modulo appindicator no encontrado, se procede de igual manera"

class Main(Plugin):
    def __init__(self, data):
        Plugin.__init__(self, data)
        self._view = data.view

    def run(self):
        self.tray=Status(self._view)
        
    def get_id(self):
        return 'tray-plugin'

class Status(gtk.StatusIcon, gobject.GObject):
    
    def __init__(self,view):
        gtk.StatusIcon.__init__(self)
        gobject.GObject.__init__(self)
        self.view=view
        self.sw = True
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
        self.set_from_icon_name ("nm-signal-25")
        self.set_tooltip('Nugget')
        self.set_visible(True)
        self.connect('activate', self.on_activate)
        self.connect('popup-menu', self.on_popup_menu)

    def on_activate(self, data):
        self.hide_or_show()
        
    def on_popup_menu(self, status, button, time):
        self.menu.popup(None, None, None, button, time)

    def on_about(self, data):
        print "no implemenado"
    
    def hide_or_show(self):
        self.sw = not self.sw
        self.view.set_visible(self.sw)
    
    def on_quit(self,data):
        print 'quit'
        gtk.main_quit()

'''class indicator_applet(gtk.StatusIcon,gobject.GObject):
    
    def __init__(self):
        self.ind = appindicator.Indicator("nugget-tray","nm-signal-00",appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status (appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon ("indicator-messages-new")
        # create a menu
        self.view=view
        self.sw=0
        
        self.menu = gtk.Menu()
        
        menu_items = gtk.MenuItem(buf[0])
        self.menu.append(menu_items)
        menu_items.show()
        menu_items.connect('activate', hide, buf[0])

        menu_items = gtk.MenuItem(buf[1])
        self.menu.append(menu_items)
        menu_items.show()
        menu_items.connect('activate', show_about_dialog,buf[1])
        
        menu_items = gtk.MenuItem(buf[2])
        self.menu.append(menu_items)
        menu_items.show()
        menu_items.connect('activate', exit,buf[2])
    
    def exit(self, text):
        print "Saliendo de Nugget"
        gtk.main_quit()
        
    def show_about_dialog(self):
        print "No implementado"
    
    def hide(self):
        if(self.sw==1):
            self.view.set_visible(True)
            self.sw=0
        else:
            self.view.set_visible(False)
            self.sw=1
            
    def mostrar(self):
        self.ind.set_menu(self.menu)

    '''
if __name__ == '__main__':
    #if(sw==0):
    #    i=indicator_applet()
    #    i.mostrar()
    #else:
    #    Status()
    Status()
    gtk.main()