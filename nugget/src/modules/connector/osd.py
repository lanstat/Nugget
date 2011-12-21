import pynotify

path = "file:///home/lance/aplicaciones/nugget/data/icons/"
img_device = path+'drive.png'
img_sms = path+'sms_new.png'
img_connected = path+'connected.png'
img_disconnected = path+'disconnected.png'

def show_device_found(modem):
	pynotify.init("Device found")
	notification = pynotify.Notification("Dispositivo encontrado",modem+'\n\n', img_device)
	notification.show()

def show_new_sms(number):
	pynotify.init("New SMS")
	notification = pynotify.Notification("Nuevo SMS",number, img_sms)
	notification.show()

def show_connected(ip, dns):
	pynotify.init("Connected")
	notification = pynotify.Notification("Coneccion establecida",'IP: '+ip+'\nDNS: '+dns, img_connected)
	notification.show()

def show_disconnect():
	pynotify.init("DisConnected")
	notification = pynotify.Notification("Desconectado correctamente",None, img_disconnected)
	notification.show()


if __name__ == "__main__":
	show_connected('10.2.3.4','20.3.42.3')
