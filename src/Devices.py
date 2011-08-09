from xml.dom.minidom import parse

class Device:
	def __init__(self):
		self.name = None
		self.vendor = None
		self.product = None
		self.dev_props = None
		self.port = {}

	def get_port(self,str):
		return self.port[str]

class DevicesAvalaible:
	def __init__(self):
		midom=parse("../data/conf/modems.xml")
		self.vendors = midom.childNodes[1].childNodes
		self.__nProduct = None
		self.__nVendor = None

	def is_device_supported(self,idVendor,idProduct):
		for vendor in self.vendors:
			if(vendor.nodeType==1):
				 if(vendor.attributes.get("id").value==idVendor):
					products = vendor.childNodes
					for product in products:
						if(product.nodeType==1):
							if(product.attributes.get("id").value==idProduct):
								self.__nProduct = product
								self.__nVendor = vendor
								return True
					break
		return False

	def get_Device(self):
		if(self.__nProduct != None):
			d = Device()
			d.name = self.__nVendor.attributes.get("name").value
			d.vendor = self.__nVendor.attributes.get("id").value
			d.product = self.__nProduct.attributes.get("id").value
			attribs = self.__nProduct.childNodes
			for attrib in attribs:
				if(attrib.nodeType == 1 and attrib.nodeName != "capabilities"):
					d.port[attrib.nodeName] = attrib.childNodes[0].data
			return d
		return None
