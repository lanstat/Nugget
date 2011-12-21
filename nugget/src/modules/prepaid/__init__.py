#coding:utf-8

import pygtk
pygtk.require20()
import gtk
import gobject

from uadh import gui, configurator
from uadh.gui import gtk2gui

from uadh.plugins import Plugin
import mobile



class Main(Plugin):
    def __init__(self, data):
        Plugin.__init__(self, data)
        self._view = data.view

    def run(self):
        s = gui.Section('Prepago', PrepaidGui(self._data))
        self._view.add_section(s)

    def get_id(self):
        return 'prepaid-plugin'

class PrepaidGui(gtk.Table):
    def __init__(self, data):
        gtk.Table.__init__(self, rows = 5, columns = 1)
        self._mainView = data.view
        self.data = data
        self.attach(ChargeGui(self),0,1,1,2, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)
        self.attach(SelectPlanGui(self),0,1,0,1, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)
        self._lblStatus = gtk.Label()
        self.attach(self._lblStatus,0,1,2,3, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)

    def send_message(self, number, message):
        terms = mobile.list_at_terminals() # list available terminals :D 
        if (len(terms)>0) and (len(number)>0) and (len(message)>0):
            dev = mobile.MobilePhone(terms[-1])
            sms = dev.create_sms(message, number)
            if sms.send():
                self.show_message('Mensaje enviado a ' + number)
                pass
            else:
                self.show_message('No se pudo enviar mensaje a ' + number)
                pass
            dev.power_off()
        else:
            if (len(terms) == 0):
                self.show_message('No se encontro dispositivo')
                return
            if (len(number) == 0):
                self.show_message('Debe introducir un telefono')
                return
            if (len(message) == 0):
                self.show_message('Debe escribir su mensaje')
                return

    def make_call(self, number):
        terms = mobile.list_at_terminals() # list available terminals :D 
        if (len(terms)>0) and (len(number)>0):
            dev = mobile.MobilePhone(terms[-1])
            if dev.call(number):
                self.show_message('Llamada exitosa a ' + number)
            else:
                self.show_message('No se pudo llamar a ' + number)
            dev.power_off()
        else:
            if (len(terms) == 0):
                self.show_message('No se encontro dispositivo')
                return
            if (len(number) == 0):
                self.show_message('Debe introducir un telefono')
                return

    def get_config(self, obj):
        terms = mobile.list_at_terminals() # list available terminals :D
        conf = None 
        if len(terms)>0:
            dev = mobile.MobilePhone(terms[-1])
            configmanager = configurator.ConfConfigurator('data/conf/countries')
            conf = configmanager.get_configuration('/' + dev.get_country_code() + '/' + dev.get_network_code() + '/prepaid.conf/' + obj)
            dev.power_off()
        return conf

    def show_message(self, text):
        self._lblStatus.set_text(text)


class ChargeGui(gtk.Frame):
    def __init__(self, gui):
        gtk.Frame.__init__(self)
        self.gui = gui
        lbl = gtk.Label()
        lbl.set_markup('<b>Cargar crédito</b>')
        self.set_shadow_type(gtk.SHADOW_NONE)
        self.set_label_widget(lbl)
        table = gtk.Table(rows = 2, columns = 3)
        table.attach(gtk.Label('Código secreto:'), 0, 1, 0, 1, xpadding = 10, ypadding = 10, xoptions=False, yoptions=False)
        self._txtSecretCode = gtk.Entry()
        table.attach(self._txtSecretCode, 1, 3, 0, 1, xpadding = 10, ypadding = 10, xoptions = gtk.EXPAND | gtk.FILL, yoptions=False)
        bbox = gtk.HButtonBox()
        self._btnCredit = gtk.Button('Ver saldo')
        self._btnData = gtk.Button('Ver consumo')
        self._btnOk = gtk.Button('Aceptar')
        self._btnCancel = gtk.Button('Cancelar')
        bbox.pack_end(self._btnCredit)
        bbox.pack_end(self._btnData)
        bbox.pack_end(self._btnOk)
        bbox.pack_end(self._btnCancel)
        self._btnCredit.connect('clicked', self.on_credit_click)
        self._btnData.connect('clicked', self.on_data_click)
        self._btnOk.connect('clicked', self.on_ok_click)
        self._btnCancel.connect('clicked', self.on_cancel_click)
        bbox.set_spacing(10)
        table.attach(bbox,0,3,1,2, xpadding = 10, ypadding = 10, xoptions=False, yoptions=False)
        self.add(table)

    def credit_charge(self):
        self.gui.show_message('')
        secret_code = self._txtSecretCode.get_text()
        if len(secret_code) > 0:
            config = self.gui.get_config('charge')
            if (config <> None):
                number = config['NUMBER']
                method_string = config['METHOD_STRING']
                method_string = method_string.replace('SECRET_CODE', secret_code)
                method_string = method_string.replace('NUMBER', number)
                if config['METHOD'] <> 'sms':
                    self.gui.make_call(method_string)
                else:
                    self.gui.send_message(number, method_string)
        else:
            self.gui.show_message('Debe introducir el codigo secreto de la tarjeta')

    def view_credit(self):
        self.gui.show_message('')
        config = self.gui.get_config('credit_query')
        if (config <> None):
            number = config['NUMBER']
            method_string = config['METHOD_STRING']
            method_string = method_string.replace('NUMBER', number)
            if config['METHOD'] <> 'sms':
                self.gui.make_call(method_string)
            else:
                self.gui.send_message(number, method_string)

    def view_data(self):
        self.gui.show_message('')
        config = self.gui.get_config('data_query')
        if (config <> None):
            number = config['NUMBER']
            method_string = config['METHOD_STRING']
            method_string = method_string.replace('NUMBER', number)
            if config['METHOD'] <> 'sms':
                self.gui.make_call(method_string)
            else:
                self.gui.send_message(number, method_string)

    def cancel(self):
        self._txtSecretCode.set_text('')
        self.gui.show_message('')

    def on_credit_click(self, *w):
        self.view_credit()

    def on_data_click(self, *w):
        self.view_data()

    def on_ok_click(self, *w):
        self.credit_charge()

    def on_cancel_click(self, *w):
        self.cancel()

class SelectPlanGui(gtk.Frame):
    def __init__(self, gui):
        gtk.Frame.__init__(self)
        self.gui = gui
        lbl = gtk.Label()
        lbl.set_markup('<b>Elegir plan</b>')
        self.set_shadow_type(gtk.SHADOW_NONE)
        self.set_label_widget(lbl)
        table = gtk.Table(rows = 4, columns = 4)
        table.attach(gtk.Fixed(),0,2,0,1, ypadding = 5, xoptions=False)
        table.attach(gtk.Label('Plan:'),0,1,1,2, xpadding = 10, ypadding = 5, xoptions=False, yoptions=False)

        frmPlan = gtk.Frame()
        lbl = gtk.Label()
        lbl.set_markup('<b>Datos del plan:</b>')
        #frmPlan.set_shadow_type(gtk.SHADOW_NONE)
        frmPlan.set_label_widget(lbl)
        self._lblPlan = gtk.Label()
        self._lblPlan.set_line_wrap(True)
        self._lblPlan.set_padding(5,5)
        frmPlan.add(self._lblPlan)
        table.attach(frmPlan,2,4,0,4, xpadding = 10, ypadding = 10)

        self._cmbPlan = gtk2gui.ComboBoxObject(gtk2gui.SecuenceViewer())
        
        self.gui.data.model.controller.connect('added_device', self.on_added_device)
        self.gui.data.model.controller.connect('removed_device', self.on_removed_device)
        self._cmbPlan.connect('show', self.on_added_device)
        self._cmbPlan.connect('changed', self.on_plan_changed)

        table.attach(self._cmbPlan,1,2,1,2, xpadding = 10, ypadding = 5, xoptions=False, yoptions=False)
        bbox = gtk.HButtonBox()
        self._btnOk = gtk.Button('Aceptar')
        self._btnOk.connect('clicked', self.on_ok_click)
        bbox.pack_end(self._btnOk)
        table.attach(bbox,0,2,2,3, xpadding = 0, ypadding = 5, xoptions=False, yoptions=False)
        table.attach(gtk.Fixed(),0,2,3,4, ypadding = 5, xoptions=False)
        #table.attach(gtk.Fixed(),3,4,1,2)
        self.add(table)

    def on_added_device(self, *w):
        self.load_plans()

    def on_removed_device(self, *w):
        self.load_plans()

    def load_plans(self):
        config = self.gui.get_config('select_plan')
        self._cmbPlan.get_model().clear()
        if (config <> None):
            options = config['OPTIONS']
            union = ','.join(options)
            if union.count('(') > 0:
                options = union
                options = options.replace('( ', '(')
                options = options.replace(') ', ')')
                options = options.replace(' (', '(')
                options = options.replace(' )', ')')
                options = [z.split(',') for z in  [ y[0].split(')')[0] for y in [x.split('),') for x in options.split('(')] if len(y)>0 and len(y[0])>0 ]]
                for opt in options:
                    self._cmbPlan.get_model().append([opt])
            else:
                options = [x.strip() for x in options]
                tuples = []
                try:
                    for opt in options:
                        config = self.gui.get_config('select_plan.' + opt)
                        tuples.append((config['NAME'], config['OPTION']))
                    for tuple in tuples:
                        self._cmbPlan.get_model().append([tuple])
                except:
                    for opt in options:
                        self._cmbPlan.get_model().append([(opt,)])


    def select_plan(self):
        try:
            selected = self._cmbPlan.get_model().get(self._cmbPlan.get_active_iter(), 0)
            selected = selected[-1][-1]
            if selected <> None or len(selected) > 0:
                config = self.gui.get_config('select_plan')
                if (config <> None):
                    number = config['NUMBER']
                    method_string = config['METHOD_STRING']
                    method_string = method_string.replace('SELECTED', selected)
                    method_string = method_string.replace('NUMBER', number)
                    if config['METHOD'] <> 'sms':
                        self.gui.make_call(method_string)
                    else:
                        self.gui.send_message(number, method_string)
            else:
                self.gui.show_message('Debe seleccionar el plan')
        except:
            self.gui.show_message('Debe seleccionar el plan')

    def show_plan(self):
        try:
            selected = self._cmbPlan.get_model().get(self._cmbPlan.get_active_iter(), 0)
            selected = selected[-1][-1]
            if selected <> None or len(selected) > 0:
                config = self.gui.get_config('select_plan.' + selected)
                if (config <> None):
                    string = config['DESCRIPTION'] + '\n<b>Costo:</b> ' + config['COST'] + '\n<b>Duración:</b> ' + config['DURATION']
                    self._lblPlan.set_markup(string)
            else:
                self.gui.show_message('Debe seleccionar el plan')
        except:
            self.gui.show_message('Debe seleccionar el plan')

    def on_ok_click(self, *w):
        self.select_plan()

    def on_plan_changed(self, *w):
        self.show_plan()
