import dbus
import os
import gobject
from Devices import *
if getattr(dbus, "version", (0,0,0)) >= (0,41,0):
	import dbus.glib

class DeviceController(gobject.GObject):

	__gsignals__ = {'added_device' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,)),
					'removed_device' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
					'support_device_detected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,())}

	def __init__(self):
		gobject.GObject.__init__(self)
		self.dbus = dbus.SystemBus()
		self.hal_manager_obj = self.dbus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
		self.hal_manager = dbus.Interface(self.hal_manager_obj, "org.freedesktop.Hal.Manager")
		
		#Signals
		self.hal_manager.connect_to_signal("DeviceAdded", self.__plug_device_cb)
		self.hal_manager.connect_to_signal("DeviceRemoved", self.__unplug_device_cb)
		
		self.devices_avalaible = DevicesAvalaible()
		self.device_active = None
		self.__first_time_hardware_detection()
		self.available_devices = []

	def __first_time_hardware_detection(self):
		self.devices = self.hal_manager.GetAllDevices()
		for dev in self.devices:
			device_dbus_obj = self.dbus.get_object("org.freedesktop.Hal", dev)
			try:
				props = device_dbus_obj.GetAllProperties(dbus_interface="org.freedesktop.Hal.Device")
			except:
				return False
			if props.has_key("info.subsystem"):
				if props["info.subsystem"] ==  "usb_device":
					if props.has_key("usb_device.product_id") and props.has_key("usb_device.product_id"):
						if  self.devices_avalaible.is_device_supported(str(props["usb_device.vendor_id"]),
																		str(props["usb_device.product_id"])):
							self.device_active = self.devices_avalaible.get_Device()
							self.device_active.dev_props = props
							print props["info.udi"]
							self.emit('added_device',self.device_active.name)
							break
		if(self.device_active!=None):
			self.get_ports()
			print self.device_active.name+" "+self.device_active.port['data']
		else:
			print "Dispositivo no encontrado"
		self.devices = []

	def get_ports(self):
		ports = []
		self.devices = self.hal_manager.GetAllDevices()
		#print "#################"
		for dev in self.devices:
			device_dbus_obj = self.dbus.get_object("org.freedesktop.Hal", dev)
			try:
				props = device_dbus_obj.GetAllProperties(dbus_interface="org.freedesktop.Hal.Device")
			except:
				return False
			if props.has_key("info.parent") and props["info.parent"] == self.device_active.dev_props["info.udi"]:
					if props.has_key("usb.linux.sysfs_path") :
						files = os.listdir(props["usb.linux.sysfs_path"])
						for f in files:
							if f.startswith("ttyUSB") :
								#print props['info.udi']
								ports.append(f)
		ports.sort()
		if(len(ports)<1):
			print "Dispositivo no reconocido por el sistema"
		else:
			data = self.device_active.port['data']
			self.device_active.port['data'] = ports[int(data)]
			conf = self.device_active.port['conf']
			self.device_active.port['conf'] = ports[int(conf)]
			print "Dispositivo reconocido "

	def __real_plug_device_cb(self, udi):
		#print "plug"
		self.devices.append(udi)
		device_dbus_obj = self.dbus.get_object("org.freedesktop.Hal", udi)
		try:
			dev_props = device_dbus_obj.GetAllProperties(dbus_interface="org.freedesktop.Hal.Device")
		except:
			return False
		if dev_props.has_key("info.subsystem"):
			if dev_props["info.subsystem"] ==  "usb_device":
				if dev_props.has_key("usb_device.product_id") and dev_props.has_key("usb_device.product_id"):
					if  self.devices_avalaible.is_device_supported(str(dev_props["usb_device.vendor_id"]),
																	str(dev_props["usb_device.product_id"])):
						self.device_active = self.devices_avalaible.get_Device()
						self.device_active.dev_props = dev_props
						self.get_ports()
						self.emit('added_device',self.device_active.name)
						print udi
						print "Dispositivo encontrado"

		return False

	def __plug_device_cb(self, udi):
		gobject.timeout_add(3000, self.__real_plug_device_cb, udi)

	def __unplug_device_cb(self, udi):
		if (self.device_active != None):
			if(self.device_active.dev_props['info.udi'] == udi):
				self.device_active = None
				self.emit('removed_device')
				print "unplug device"
