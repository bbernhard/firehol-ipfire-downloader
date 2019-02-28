import shutil
import urllib2
import subprocess
import shlex
import sys
import logging
import os

if __name__ == "__main__":
	log_file = "/tmp/firehol.log"
	log_format = "%(asctime)s [%(levelname)-5.5s]  %(message)s" 
	fhandler = logging.FileHandler(filename=log_file)
	fhandler.setFormatter(logging.Formatter(log_format))
	
	shandler = logging.StreamHandler()	

	logger = logging.getLogger(__name__)

	logger.addHandler(fhandler)
	logger.addHandler(shandler)

	logger.info("Downloading file...")
	headers = hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       			 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       			 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       			 'Accept-Encoding': 'none',
       			 'Accept-Language': 'en-US,en;q=0.8',
       			 'Connection': 'keep-alive'}
	url = 'https://iplists.firehol.org/files/firehol_level1.netset'  
	req = urllib2.Request(url, headers=hdr)
	
	data = None
	try:
		data = urllib2.urlopen(req)  
	except:
		logger.error("Couldn't download firehol data...exiting")
		sys.exit(1)
	
	destination = "/tmp/firehol_level1.netset"
	with open(destination, 'wb') as f:
		f.write(data.read())		  

	logger.info("Stop firewall.local")
	ret = subprocess.call(shlex.split("/etc/sysconfig/firewall.local stop"))
	if ret != 0:
		logger.error("Couldn't stop firewall.local...aborting")
		sys.exit(1)

	logger.info("Remove existing firehol ipset")
	subprocess.call(shlex.split("/usr/sbin/ipset destroy firehol"))


	logger.info("Creating firehol ipset")
	subprocess.call(shlex.split("/usr/sbin/ipset create firehol hash:net"))


	logger.info("Reading firehol list")
	with open(destination) as fp:
		lines = fp.readlines()
		for line in lines:
			if line.startswith("#"):
				continue
			if line.startswith("192.168"):
				continue
			if line.startswith("127.0.0.0/8"):
				continue
			print("add %s" %line)
			ret = subprocess.call(shlex.split("/usr/sbin/ipset add firehol %s" %line))
			if ret != 0:
				logger.error("ERROR: Couldn't add rule")
	
	ret = subprocess.call(shlex.split("/etc/sysconfig/firewall.local start"))
	if ret != 0:
		logger.error("Coudln't start firewall.local...aborting")
		sys.exit(1)	
