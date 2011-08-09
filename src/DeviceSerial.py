import serial
import gobject

class DeviceSerial:
	def __init__(self):
		self.serialPort= None
		self.sw = False
		self.str1 = ""
		self.msg = ['COMMAND NOT SUPPORT\r','OK\r','ERROR\r','NO CARRIER\r']
		self.__response = ""
		self.is_connect = False

	def connect(self,port1):
		self.serialPort = serial.Serial(port='/dev/'+port1,baudrate=115200,timeout=5,rtscts=0,xonxoff=0)
		self.is_connect = True
		self.serialPort.open()

	def __reading(self):
		if(self.sw==True):
			car = self.serialPort.read()
			self.str1 = self.str1+car
			if(car == '\n'):
				#print self.str1
				sp = self.str1.split('\n')
				#print sp
				if(sp[-2] in self.msg ):
					print self.str1
					self.str1 = ""
					self.__response = sp[-2]
					return False
				self.sw=True
			if(car=='>'):
				print car
				self.str1 = ""
				return False
			return True
		else:
			print self.str1
			return False

	def __send_command(self,command,data=None):
		if(data == None):
			self.serialPort.write("AT"+command+"\r")
		else:
			self.serialPort.write(command+chr(26))
		print "Procesando comando AT"+command+"..."
		print "\n"
		self.sw = True
		gobject.timeout_add(50,self.__reading)

	def close(self):
		self.is_connect = False
		self.serialPort.close()

	def activate(self):
		self.__send_command("")

	def get_addressbook(self):
		
