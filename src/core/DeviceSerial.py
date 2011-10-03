import gobject
from mobile import *

class PhoneData(gobject.GObject):

	__gsignals__ = {'new_sms' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
					'signal_update' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_INT,))}
	
	def __init__(self, port="ttyUSB1"):
		gobject.GObject.__init__(self)
		dev = ATTerminalConnection("/dev/"+port)
		self.__phone = None
		self.__device = None
		if(dev != None):
			self.__phone = MobilePhone(dev)
			self.__device = MobileDevice(dev)
			gobject.timeout_add_seconds(20,self.__check_device)

	def get_signal(self):
		return self.__device.get_signal_strenght()

	def __check_device(self):
		signal = self.__device.get_signal_strenght() 
		self.emit('signal_update',signal)
		sms = self.__device.list_new_sms()
		if(len(sms)>0):
			self.emit('new_sms')
		
		return True

	def get_addressbook(self):
		address_book = self.__phone.get_phonebook()
		return address_book

	def get_old_sms(self):
		return self.__device.list_old_sms()

	def get_new_sms(self):
		return self.__device.list_new_sms()

	def is_active(self):
		return (self.__phone != None)

	def send_sms(self, message, phone):
		sms = self.__device.create_sms(message,phone)
		sms.send()
