try:
	import os
	from __init__ import operator
except Exception, detail:
	print detail
from subprocess import Popen, PIPE
import gobject
import time
from Status import *
from random import random

class monitor(gobject.GObject):

	__gsignals__ = {'connecting' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
					'connected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
					'disconnecting' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
					'disconnected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,()),
					'connecting_state_change' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,)),
					'pppstats_signal' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_INT,gobject.TYPE_INT,
										gobject.TYPE_INT,))}
	
	def __init__(self):
		gobject.GObject.__init__(self)
		self.wvdial_conf_file = '/var/tmp/dialer.conf'
		self.wvdial_p = None
		self.wvdial_pid = None
		self.pppd_pid = None
		self.ppp_if = None
		self.last_traffic_time = 0.0
		self.dns_data = None
		self.select_operator = None
		self.status_flag = PPP_STATUS_DISCONNECTED
		#gobject.timeout_add_seconds(2,self.__algo)

	def __algo(self):
		up = random()*150
		down = random()*150
		self.emit('pppstats_signal',int(down),int(up),1)
		return True

	def __create_config(self, modem_active):
		wvdial_conf = "[Dialer Defaults]\n"
		wvdial_conf = wvdial_conf + "Modem = /dev/%s\n" % modem_active
		phone = "*99#"
		if(self.__select_operator.get_attrib("phone")!=""):
			phone = self.__select_operator.get_attrib("phone")
		wvdial_conf = wvdial_conf + "Phone = %s\n" % phone
		wvdial_conf = wvdial_conf + "Username = '%s'\n" % self.__select_operator.get_attrib("username")
		wvdial_conf = wvdial_conf + "Password = '%s'\n" % self.__select_operator.get_attrib("password")
		os.system("rm -f %s" % self.wvdial_conf_file)
		fd = open(self.wvdial_conf_file, "w")
		fd.write(wvdial_conf)
		fd.close()
		self.__start_wvdial()

	def status(self):
		return self.status_flag

	def __start_wvdial(self):
		print "Starting Wvdial"
		self.status_flag = PPP_STATUS_CONNECTING
		self.emit('connecting')
		
		cmd = "/usr/bin/wvdial -C %s" % self.wvdial_conf_file
		self.wvdial_p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,stderr=PIPE, close_fds=True)
		gobject.timeout_add(1, self.__wvdial_monitor)
		gobject.timeout_add(3000, self.__pppd_monitor)

	def __get_real_wvdial_pid(self):
		cmd = "ps -eo ppid,pid | grep '^[ ]*%s' | awk '{print $2}'" % self.wvdial_p.pid
		pm =  Popen(cmd, shell=True, stdout=PIPE, close_fds=True)

		ret = pm.stdout.readline().strip("\n")
		if ret != "" :
			return ret
		else:
			return None

	def __wvdial_monitor(self):
		self.__real_wvdial_monitor()
		gobject.timeout_add(2000, self.__real_wvdial_monitor)
		return False

	def __real_wvdial_monitor(self):
		if self.wvdial_p.poll() == None :
			print "Wvdial monitor : Wvdial running"
			return True
		else:
			print  "Wvdial monitor : Wvdial killed"
			self.wvdial_p = None
			self.wvdial_p = None
			self.wvdial_pid = None
			self.pppd_pid = None
			self.ppp_if = None
			self.last_traffic_time = 0.0
			self.dns_data = None
			self.status_flag = PPP_STATUS_DISCONNECTED

			print "emit disconnected"
			self.emit('disconnected')

			return False

	def __pppd_monitor(self):
		if self.status_flag == PPP_STATUS_DISCONNECTING or self.status_flag == PPP_STATUS_DISCONNECTED :
			print "pppd monitor stopped, status disconnecting or disconected"
			self.pppd_pid == None
			self.ppp_if = None
			return False

		if self.wvdial_p == None:
			print "pppd monitor stopped, not wvdial running"
			return False
		elif self.wvdial_p.poll() != None:
			print "pppd monitor stopped, not wvdial running"
			return False

		if self.pppd_pid == None :
			if self.wvdial_pid == None :
				if os.path.exists("/etc/debian_version") :
					self.wvdial_pid = self.__get_real_wvdial_pid()
				else:
					self.wvdial_pid = self.wvdial_p.pid
				print "--------> WVDIAL PID %s" % self.wvdial_pid
				if self.wvdial_pid == None :
					return True

			print  "pppd monitor : looking for pppd"
			self.emit('connecting_state_change','Creando pppd')
			cmd = "ps -eo ppid,pid | grep '^[ ]*%s' | awk '{print $2}'" % self.wvdial_pid
			pm =  Popen(cmd, shell=True, stdout=PIPE, close_fds=True)

			pppd_pid = pm.stdout.readline().strip("\n")

			if pppd_pid != "" :
				self.pppd_pid = pppd_pid
				print "--------> PPPD PID %s" % self.pppd_pid
				self.emit('connecting_state_change',"Buscando IP...")

				wvdial_stderr = self.wvdial_p.stderr
				while True:
					tmp_str = wvdial_stderr.readline()
					if "Using interface" in tmp_str :
						self.ppp_if = tmp_str.split()[-1]
						print  "pppd monitor : %s" % self.ppp_if
						break

			return True
		elif self.ppp_if != None :
			print  "pppd monitor : looking for ip"
			self.emit('connecting_state_change','Buscando IP...')
			cmd = "LANG=C ifconfig %s | grep 'inet addr'" % self.ppp_if
			pm =  Popen(cmd, shell=True, stdout=PIPE, close_fds=True)
			out = pm.stdout.readline()
			if out != "" :
				print  "pppd monitor : pppd connected"
				self.__set_dns_info()
				self.status_flag = PPP_STATUS_CONNECTED
				self.emit('connected')
				gobject.timeout_add(2000, self.__stats_monitor)
				return False
			else:
				return True
		else:
			return True

	def start(self, current_op, modem_active):
		print "DAEMON ----> INIT"
		if self.status_flag != PPP_STATUS_DISCONNECTED :
			return 
		self.__select_operator = current_op
		self.__create_config(modem_active)

	def stop(self):
		print "Stopping pppd"

		if self.wvdial_p == None:
			print "Stop : no wvdial_p"  
			return
		elif self.wvdial_p.poll() != None:
			print "Stop : wvdial_p.poll() != None"
			return
			
		
		if self.wvdial_pid != None :
			print "emit disconnecting"
			self.emit('disconnecting')
			self.status_flag = PPP_STATUS_DISCONNECTING
			print "kill -15 %s" % self.wvdial_pid
			os.kill(int(self.wvdial_pid), 15)
			
		elif self.wvdial_p != None :
			if os.path.exists("/etc/debian_version") :
				self.wvdial_pid = self.__get_real_wvdial_pid()
			else:
				self.wvdial_pid = self.wvdial_p.pid
			
			self.emit('disconnecting')
			print "emit disconnecting"
			self.status_flag = PPP_STATUS_DISCONNECTING
			
			print "kill -15 %s" % self.wvdial_pid
			os.kill(int(self.wvdial_pid), 15)

	def __set_dns_info(self):
		print "-----> __set_dns_info (%s)" % self.dns_data
		if self.dns_data == None :
			return
		
		os.system("echo ';Nugget manager dns data' > /etc/resolv.conf")
		if self.dns_data[2] != "" :
			os.system("echo 'search %s' >> /etc/resolv.conf" % self.dns_data[2])

		if self.dns_data[0] != "" :
			os.system("echo 'nameserver %s' >> /etc/resolv.conf" % self.dns_data[0])

		if self.dns_data[1] != "" :
			os.system("echo 'nameserver %s' >> /etc/resolv.conf" % self.dns_data[1])

	def __parse_stats_response(self):
		cmd = "cat /proc/net/dev | grep %s | sed s/.*://g | awk '{print $1; print $9}'" % self.ppp_if
		pm =  Popen(cmd, shell=True, stdout=PIPE, close_fds=True)
		rb = pm.stdout.readline().strip("\n")
		tb = pm.stdout.readline().strip("\n")

		if rb == "" and tb == "" :
			return 0, 0
		else:
			return int(rb) , int(tb)   

	def __stats_monitor(self):
		if self.status_flag == PPP_STATUS_DISCONNECTING or self.status_flag == PPP_STATUS_DISCONNECTED :
			print "stats monitor stopped, status flag disconnecting or disconnected"
			return False
			
		if self.wvdial_p == None:
			print "stats monitor stopped, not wvdial running"
			return False
		elif self.wvdial_p.poll() != None:
			print "stats monitor stopped, not wvdial running"
			return False
		
		if self.ppp_if == None :
			return False
		
		recived_bytes , sent_bytes = self.__parse_stats_response()
		if self.last_traffic_time == 0.0 :
			self.last_traffic_time = time.time()
		else:
			if recived_bytes > 0 and sent_bytes > 0 :
				new_time = time.time()
				interval_time = new_time - self.last_traffic_time
				self.last_traffic_time = new_time
				if self.status_flag == PPP_STATUS_CONNECTED :
					self.emit("pppstats_signal", recived_bytes, sent_bytes, interval_time)
					print "stats monitor : %i %i %d" % (recived_bytes, sent_bytes, interval_time)

		return True
