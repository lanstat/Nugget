
class operator:
	def __init__(self):
		self.__attrib={}
		self.__attrib["name"]=""
		self.__attrib["phone"]=""
		self.__attrib["username"]=""
		self.__attrib["password"]=""
		self.__attrib["logo"]=""
		self.__attrib["stupid_mode"]=""
	
	def add(self,atr,data):
		self.__attrib[atr]=data
	
	def get_attrib(self,atr):
		return self.__attrib[atr]
