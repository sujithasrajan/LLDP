from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import RpcError
from jnpr.junos.utils.config import Config
from graphviz import Graph
from lxml import etree as etree
import yaml
import json 

host_ip = ['192.168.1.35', '192.168.1.36', '192.168.1.37', '192.168.1.38','192.168.1.39','192.168.1.40']
if_config = {'192.168.1.35': {'ge-0/0/1':'72.114.97.0/19', 'ge-0/0/2':'72.114.129.0/19'}, 
	     '192.168.1.36': {'ge-0/0/1':'72.114.130.0/19', 'ge-0/0/2':'72.114.162.0/19'},
	     '192.168.1.37': {'ge-0/0/1':'72.114.193.0/19', 'ge-0/0/2':'72.114.98.0/19', 'ge-0/0/3':'72.114.163.0/19','ge-0/0/4':'72.114.225.0/19'},
	     '192.168.1.38': {'ge-0/0/1':'72.114.255.2/19', 'ge-0/0/2':'72.114.226.0/19'},
	     '192.168.1.39': {'ge-0/0/1':'72.114.255.3/19', 'ge-0/0/2':'72.114.194.0/19', 'ge-0/0/3':'72.114.255.34/19'},
	     '192.168.1.40': {'ge-0/0/1':'72.114.255.35/19'} }

neighbor_info = {}
info_dict = {}
topo_list = []
router_list = []
info_dict_list=[]

def make_topo(info_dict_list):
	#seperating nodes and edges from the dictionary
	device_list=[]
	for device in info_dict_list:
		nodes = [device['nodes']]
		edges=[]
		for neighbor in device['neighbor']:
			nodes.append(neighbor['Remote host name'])
			edges.append([device['nodes'],neighbor['Remote host name'], neighbor['Local interface'], neighbor['Remote host interface']]) 
		device_list.append((nodes,edges))
	#delete any repeated nodes and edges
	nodes = []
	edges = []
	for var in device_list:
		for node in var[0]:
			if node not in nodes:
				nodes.append(node)
		for edge in var[1]:
			edges.append(edge)
	#graph creation
	dot= Graph(comment = "My Network Topology" , format = 'png', strict = True)
	dot.graph_attr['splines'] = 'ortho'
	for i in nodes:
		dot.node(i, shape = 'circle')
	for i in edges:
		dot.attr('edge', headlabel=i[2], taillabel=i[3], fontsize = '10', dir = 'both')
		dot.edge(i[0], i[1])
	return dot
	

try:
	for i,j in zip(host_ip, range(len(host_ip))):
		print(i, j)
		device = Device(host=i, user='labuser', password='Labuser', normalize=True)
		device.open()
		device.bind(conf=Config)
		var_dict = {'if_config': if_config[i] }
		device.conf.load(template_path='template_lldp.conf', template_vars = var_dict, merge = True)

		success = device.conf.commit()
		print("Success : {}".format(success))
		test = device.rpc.get_lldp_neighbors_information()
		test1 = device.rpc.get_config()
		info = test.findall("lldp-neighbor-information")
		local_router = test1.findall("system")
		for router in local_router:
			router_list.append(router[0].text)
			neighbor_info_list = []
			for info1 in info:
				neighbor_info={"Local interface" : info1[0].text, "Remote host name" : info1[5].text, "Remote host interface" : info1[4].text}
				neighbor_info_list.append(neighbor_info)
			info_dict = {'nodes':router[0].text , 'neighbor': (neighbor_info_list)}
			info_dict_list.append(info_dict)
	dot = make_topo(info_dict_list)
	dot.render(filename='MyTopology')


except (RpcError, ConnectError) as err:
	print("\nError: " + repr(err))

finally:
	device.close()
