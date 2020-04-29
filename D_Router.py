from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import RpcError
from jnpr.junos.utils.config import Config
from lxml import etree as etree
import time
import yaml

device = Device(host='192.168.1.24', user='labuser', password='Labuser', normalize=True)
if_config = {'ge-0/0/1':'72.114.253.68', 'ge-0/0/2':'72.114.255.5', 'ge-0/0/3':'72.114.131.0'}
if_config_check = {'ge-0/0/1': 'passive', 'ge-0/0/2':'', 'ge-0/0/3' : '' }
if_area = {'ge-0/0/1':'area 0.0.0.20', 'ge-0/0/2':'area 0.0.0.20', 'ge-0/0/3':'area 0.0.0.0'}
var_dict = {'if_config':if_config, 'if_config_check': if_config_check, 'if_area' : if_area}

try:
	device.open()
	device.bind(conf=Config)
	device.conf.load(template_path='temp1.conf', template_vars = var_dict, merge = True)
	success = device.conf.commit()
	print("Success : {}".format(success))
	test = device.rpc.get_lldp_neighbors_information()
	info = test.findall("lldp-neighbor-information")
	for info1 in info:
		print("Local interface name is: {} \nRemote interface name is: {} \nRemote host name is: {} \n".format(info1[0].text, info1[4].text, info1[5].text))


except (RpcError, ConnectError) as err:
	print("\nError: " + repr(err))

finally:
	device.close()
