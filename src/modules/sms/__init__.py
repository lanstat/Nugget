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
        s = gui.Section('Sms',SmsGui(self._data))
        self._view.add_section(s)

    def get_id(self):
        return 'sms-plugin'

class SmsGui(gtk.Notebook):
    def __init__(self, data):
        gtk.Notebook.__init__(self)
        self.set_border_width(5)
        self.data = data
        self.view = data.view
        self.sendgui = SmsSendGui(self)
        self.receivegui = SmsReceiveGui(self)
        self.append_page(self.sendgui, gtk.Label('Enviar'))
        self.append_page(self.receivegui, gtk.Label('Recibir'))
        self.set_tab_pos(gtk.POS_LEFT)
        self.connect('switch-page', self.load_gui)
        self.data.model.controller.connect('added_device', self.on_added_device)
        self.data.model.controller.connect('removed_device', self.on_removed_device)

    def on_added_device(self, m_controller, dev):
        self.load_gui()

    def on_removed_device(self, m_controller):
        self.load_gui()

    def load_gui(self, *w):
        self.sendgui.load_contacts()
        self.receivegui.load_messages()

    def get_data_port(self):
        try:
            return '/dev/' + self.data.model.controller.device_active.port['data']
        except:
            return ''



class SmsSendGui(gtk.Table):
    def __init__(self, smsgui):
        gtk.Table.__init__(self, rows = 8, columns = 7)
        self.smsgui = smsgui
        self.attach(gtk.Label('Para:'), 0, 1, 0, 1, ypadding = 5, xoptions=False, yoptions=False)
        self._txtNumber = gtk.Entry()
        self.attach(self._txtNumber, 1, 3, 0, 1, xpadding = 5, ypadding = 5, xoptions = gtk.FILL, yoptions=False)
        self._btnOpen = gtk.Button('Abrir')
        self._btnOpen.connect('clicked', self.on_open_clicked)
        self.attach(self._btnOpen, 3, 4, 0, 1, xpadding = 5, ypadding = 5, yoptions=False)
        
        self.attach(gtk.Label('Mensaje:'), 0, 1, 1, 2, ypadding = 5, xoptions=False, yoptions=False)
        self.attach(gtk.Fixed(), 0, 1, 2, 3)
        
        self._txtMessage = gtk.TextBuffer()
        self._txtMessage.connect('changed', self.on_text_message_changed)
        tview = gtk.TextView(self._txtMessage)
        tview.set_wrap_mode(gtk.WRAP_WORD)
        scroll = gtk.ScrolledWindow()
        scroll.add(tview)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.attach(scroll, 1, 4, 1, 5, xpadding = 5, ypadding = 5)
        
        self._lstPhoneBook = gtk2gui.ListView('Contactos', gtk2gui.ObjectViewer())
        self._lstPhoneBook.connect('row-selected', self.on_list_clicked)
        scroll = gtk.ScrolledWindow()
        scroll.add(self._lstPhoneBook)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.attach(scroll, 4, 7, 0, 8, xpadding = 5, ypadding = 5)
        
        bbox = gtk.VButtonBox()
        self._btnShort = gtk.Button('Acortar SMS')
        self._btnShort.connect('clicked', self.on_short_clicked)
        self._btnView = gtk.Button('Ver SMS a enviar')
        self._btnView.connect('clicked', self.on_view_clicked)
        bbox.pack_end(self._btnShort)
        bbox.pack_end(self._btnView)
        bbox.set_spacing(5)
        self.attach(bbox, 0, 1, 3, 4, xpadding = 0, ypadding = 0, xoptions=False, yoptions=False)
        
        self.attach(gtk.Fixed(), 0, 1, 4, 5)
        
        bbox = gtk.HButtonBox()
        self._btnSend = gtk.Button('Enviar')
        self._btnSend.connect('clicked', self.on_send_clicked)
        self._btnCancel = gtk.Button('Cancelar')
        self._btnCancel.connect('clicked', self.on_cancel_clicked)
        bbox.pack_end(self._btnSend)
        bbox.pack_end(self._btnCancel)
        bbox.set_spacing(10)
        self.attach(bbox, 0, 4, 5, 6, xpadding = 5, ypadding = 5, xoptions=False, yoptions=False)
        
        self._lblStatus = gtk.Label('')
        self.attach(self._lblStatus, 0, 4, 6, 7, xpadding = 5, ypadding = 5, xoptions=False, yoptions=False)
        self.load_contacts()

    def load_contacts(self):
        terms = mobile.list_at_terminals() # list available terminals :D
        if len(terms)>0:
            dev = mobile.MobilePhone(terms[-1])
            self._lstPhoneBook.clear()
            self._lstPhoneBook.add_all(dev.get_phonebook())
            dev.power_off()
            self._lblStatus.set_text('Listo')
        else:
            self._lblStatus.set_text('No se encontro dispositivo')

    def add_number(self, number):
        num = self._txtNumber.get_text()
        num.strip()
        if (num.count(number) > 0):
            return
        if len(num)>0:
            num = num + ', ' + number
        else:
            num = number
        self._txtNumber.set_text(num)

    def set_message(self, message):
        self._txtMessage.set_text(message)

    def get_message(self):
        return self._txtMessage.get_text(self._txtMessage.get_start_iter(), self._txtMessage.get_end_iter())

    def send_message(self):
        terms = mobile.list_at_terminals() # list available terminals :D    
        numbers = self._txtNumber.get_text()
        message = self._txtMessage.get_text(self._txtMessage.get_start_iter(), self._txtMessage.get_end_iter()) 
        if (len(terms)>0) and (len(numbers)>0) and (len(message)>0):
            dev = mobile.MobilePhone(terms[-1])
            numbers = numbers.split(',')
            for number in numbers:
                sms = dev.create_sms(message, number)
                if sms.send():
                    self._lblStatus.set_text('Mensaje enviado a ' + number)
                else:
                    self._lblStatus.set_text('No se pudo enviar mensaje a ' + number)
            dev.power_off()
        else:
            if (len(terms) == 0):
                self._lblStatus.set_text('No se encontro dispositivo')
                return
            if (len(numbers) == 0):
                self._lblStatus.set_text('Debe introducir un telefono')
                return
            if (len(message) == 0):
                self._lblStatus.set_text('Debe escribir su mensaje')
                return

    def cancel_message(self):
        self._txtMessage.set_text('')
        self._txtNumber.set_text('')
        self._lblStatus.set_text('')

    def load_from_file(self, filename):
        f = open(filename)
        for line in f:
            line = line.replace('\n','')
            line = line.replace('\r','')
            self.add_number(line)

    def set_sms(self, number, message):
        self._txtNumber.set_text(number)
        self._txtMessage.set_text(message)

    def transform_to_short_sms(self, message):
        dictionary = {'de':'d', 'para':'pa', 'que':'q', ':-D': ':D', ':-)':':)', ';-)':';)', ';-D':';D', ';-*':';*', ':-*':':*', 'te quiero mucho':'tkm', 'te':'t'}
        message = ' ' + message + ' '
        for (key, value) in dictionary.items():
            message = message.replace(' ' + key + ' ', ' ' + value + ' ')
        return message.strip()

    def message_shortener(self):
        self.set_message(self.transform_to_short_sms(self.get_message()))

    def view_sending_messages(self):
        pass

    def on_list_clicked(self, widget, elem):
        self.add_number(elem.get_phone_number())

    def on_send_clicked(self, *w):
        self.send_message()

    def on_cancel_clicked(self, *w):
        self.cancel_message()

    def on_open_clicked(self, *w):
        fileopen = gtk.FileChooserDialog('abrir', self.smsgui.view, action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("text/txt")
        filter.add_mime_type("text/txt")
        filter.add_pattern("*.txt")
        fileopen.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        fileopen.add_filter(filter)
        response = fileopen.run()     
        fileopen.hide()
        if response == gtk.RESPONSE_OK:
            filename = fileopen.get_filename()
            self.load_from_file(filename)
        fileopen.destroy()

    def on_text_message_changed(self, *w):
        msg = self.get_message()
        smscount = ((len(msg) -1) / mobile.SMS_ASCII_LENGHT) +1
        lenremaining = (mobile.SMS_ASCII_LENGHT - (len(msg) % mobile.SMS_ASCII_LENGHT)) % mobile.SMS_ASCII_LENGHT
        txt = "Sms's: %i \nCaracteres Restantes: %i" % (smscount, lenremaining)
        self._lblStatus.set_text(txt)

    def on_short_clicked(self, *w):
        self.message_shortener()

    def on_view_clicked(self, *w):
        pass



class SmsReceiveGui(gtk.Table):
    def __init__(self, smsgui):
        gtk.Table.__init__(self, rows = 6, columns = 6)
        self.smsgui = smsgui
        self.attach(gtk.Label('De:'), 2, 3, 0, 1, ypadding = 5, xoptions=False, yoptions=False)
        self._txtNumber = gtk.Entry()
        self._txtNumber.set_property('editable', False)
        self.attach(self._txtNumber, 3, 4, 0, 1, xpadding = 5, ypadding = 5, yoptions=False)
        
        self.attach(gtk.Label('Fecha:'), 2, 3, 1, 2, ypadding = 5, xoptions=False, yoptions=False)
        self._lblDate = gtk.Label('')
        self.attach(self._lblDate, 3, 4, 1, 2, ypadding = 5, xoptions=False, yoptions=False)
        
        self.attach(gtk.Label('Mensaje:'), 2, 3, 2, 3, ypadding = 5, xoptions=False, yoptions=False)
        self.attach(gtk.Fixed(), 2, 3, 3, 4)
        
        self._txtMessage = gtk.TextBuffer()
        tview = gtk.TextView(self._txtMessage)
        tview.set_property('editable', False)
        tview.set_wrap_mode(gtk.WRAP_WORD)
        scroll = gtk.ScrolledWindow()
        scroll.add(tview)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.attach(scroll, 3, 6, 2, 4, xpadding = 5, ypadding = 5)
        
        self._lstMessages = gtk2gui.ListView('Mensajes', gtk2gui.ObjectViewer())
        self._lstMessages.connect('row-selected', self.on_list_clicked)
        scroll = gtk.ScrolledWindow()
        scroll.add(self._lstMessages)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.attach(scroll, 0, 2, 0, 6, xpadding = 5, ypadding = 5)
        
        bbox = gtk.HButtonBox()
        self._btnResponse = gtk.Button('Responder')
        self._btnResponse.connect('clicked', self.on_response_clicked)
        self._btnResponse.set_sensitive(False)
        self._btnResend = gtk.Button('Reenviar')
        self._btnResend.connect('clicked', self.on_resend_clicked)
        self._btnResend.set_sensitive(False)
        self._btnDelete = gtk.Button('Eliminar')
        self._btnDelete.connect('clicked', self.on_delete_clicked)
        self._btnDelete.set_sensitive(False)
        bbox.pack_end(self._btnResponse)
        bbox.pack_end(self._btnResend)
        bbox.pack_end(self._btnDelete)
        bbox.set_spacing(10)
        self.attach(bbox, 2, 6, 4, 5, xpadding = 5, ypadding = 5, xoptions=False, yoptions=False)
        self._lblStatus = gtk.Label('')
        self.attach(self._lblStatus, 2, 6, 5, 6, xpadding = 5, ypadding = 5, xoptions=False, yoptions=False)
        self.load_messages()

    def load_messages(self):
        terms = mobile.list_at_terminals() # list available terminals :D    
        if len(terms)>0:
            '''
            port = None
            for term in terms:
                if str(term) <> self.smsgui.get_data_port():
                    port = term
                    break
            if port == None:
                return
            dev = mobile.MobilePhone(port)
            '''
            dev = mobile.MobilePhone(terms[-1])
            self._lstMessages.clear()
            self._lstMessages.add_all(dev.list_sms())
            dev.power_off()
            self._lblStatus.set_text('Listo')
        else:
            self._lblStatus.set_text('No se encontro dispositivo')

    def add_number(self, number):
        self._txtNumber.set_text(number)

    def set_message(self, message):
        self._txtMessage.set_text(message)

    def set_date(self, date):
        date = self.__get_date_string(date)
        self._lblDate.set_markup('<b>' + date + '</b>')
    
    def __get_date_string(self, date):
        datetimelist = date.split(',')
        datetimelist[-1] = datetimelist[-1][:-3]
        datelist = datetimelist[0].split('/')
        datelist[0] = str( 2000 + int(datelist[0]))
        monthdic= {'01': 'ene', '02':'feb', '03':'mar', '04':'abr', '05':'may', '06':'jun', '07':'jul', '08':'ago', '09':'sep', '10':'oct', '11':'nov', '12':'dic'}
        datelist[1] = monthdic[datelist[1]]
        datelist[2] = datelist[2]        
        return  ' de '.join(datelist[::-1]) + ' ' + datetimelist[-1]

    def on_list_clicked(self, widget, elem):
        self.sms = elem
        if self.sms == None:
            return
        self.add_number(self.sms.get_phone_number())
        self.set_date(self.sms.get_date())
        self.set_message(self.sms.get_message())
        self._btnDelete.set_sensitive(True)
        self._btnResend.set_sensitive(True)
        self._btnResponse.set_sensitive(True)

    def on_resend_clicked(self, *w):
        self.resend_message()

    def on_delete_clicked(self, *w):
        self.delete_message()

    def on_response_clicked(self, *w):
        self.response_message()

    def resend_message(self):
        if self.sms == None:
            return
        message = self.sms.get_message()
        self.smsgui.sendgui.set_sms('', message)
        self.smsgui.set_current_page(0)

    def delete_message(self):
        if self.sms == None:
            return
        terms = mobile.list_at_terminals() # list available terminals :D
        if len(terms)>0:
            dev = mobile.MobilePhone(terms[-1])
            dev.delete_sms(self.sms)
            dev.power_off()
            self._lblStatus.set_text('Mensaje eliminado')
            self.sms = None
            self.load_messages()
            self._btnDelete.set_sensitive(False)
            self._btnResend.set_sensitive(False)
            self._btnResponse.set_sensitive(False)
            self.set_message('')
            self.add_number('')
            self._lblDate.set_text('')
            self._lblStatus.set_text('Listo')
        else:
            self._lblStatus.set_text('No se encontro dispositivo')

    def response_message(self):
        if self.sms == None:
            return
        number = self.sms.get_phone_number()
        self.smsgui.sendgui.set_sms(number, '')
        self.smsgui.set_current_page(0)

    def clear(self):
        self._txtMessage.set_text('')
        self._txtNumber.set_text('')
        self._lblStatus.set_text('')
