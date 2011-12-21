import dbus
import os
import gobject
from Devices import *
import pyudev
from pyudev.glib import GUDevMonitorObserver

class DeviceController(gobject.GObject):

    __gsignals__ = {'added_device' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,)),
                    'removed_device' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,())}

    def __init__(self):
        gobject.GObject.__init__(self)
        
        self.context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(self.context)
        observer = GUDevMonitorObserver(monitor)
        observer.connect("device-added", self.__plug_device_cb)
        observer.connect("device-removed", self.__unplug_device_cb)
        
        self.devices_avalaible = DevicesAvalaible()
        self.device_active = None
        self.__first_time_hardware_detection()
        self.available_devices = []
        monitor.enable_receiving()
        
    def __first_time_hardware_detection(self):
        for device in self.context.list_devices(subsystem='usb'):        
            attr = device.attributes
            try:
                if(attr['idVendor']!=None):
                    if self.devices_avalaible.is_device_supported(attr['idVendor'],attr['idProduct']):
                        self.device_active = self.devices_avalaible.get_Device()
                        self.emit('added_device',self.device_active.name)
                        break
            except Exception:
                pass
        if(self.device_active!=None):
            self.get_ports()
            print self.device_active
        else:
            print "Dispositivo no encontrado"
        self.devices = []
    
    def get_ports(self):
        ports=[]
        for device in self.context.list_devices(subsystem='usb-serial'):
            ports.append(device.sys_name)
        ports.sort()
        if(len(ports)<1):
            print "Dispositivo no reconocido por el sistema"
            self.device_active = None
        else:
            try:
                data = self.device_active.port['data']
                self.device_active.port['data'] = ports[int(data)]
            except:
                pass
            try:
                conf = self.device_active.port['conf']
                self.device_active.port['conf'] = ports[int(conf)]
            except:
                pass
            print "Dispositivo reconocido "
            self.emit('added_device',self.device_active.name)


    def __plug_device_cb(self, monitor, device):
        attr = device.attributes
        try:
            if(attr['idVendor'] != None):
                if self.devices_avalaible.is_device_supported(attr['idVendor'],attr['idProduct']):
                    self.device_active = self.devices_avalaible.get_Device()
                    self.emit('added_device',self.device_active.name)
        except Exception:
            pass
        

    def __unplug_device_cb(self, udi):
        if (self.device_active != None):
            if(self.device_active.dev_props['info.udi'] == udi):
                self.device_active = None
                self.emit('removed_device')
                print "unplug device"
