from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import RpcError
from jnpr.junos.utils.config import Config
from graphviz import Graph
#from graphviz import Source
from lxml import etree as etree
import yaml
import json 


host_ip = ['192.168.1.19', '192.168.1.20', '192.168.1.21', '192.168.1.22','192.168.1.23']
#configurations of the interfaces
if_config = {'192.168.1.19': {'ge-0/0/1':'72.114.97.0/19', 'ge-0/0/2':'72.114.129.0/19'}, 
	     '192.168.1.20': {'ge-0/0/1':'72.114.130.0/19', 'ge-0/0/2':'72.114.162.0/19'},
	     '192.168.1.21': {'ge-0/0/1':'72.114.193.0/19', 'ge-0/0/2':'72.114.98.0/19', 'ge-0/0/3':'72.114.163.0/19','ge-0/0/4':'72.114.225.0/19'},
	     '192.168.1.22': {'ge-0/0/1':'72.114.255.2/19', 'ge-0/0/3':'72.114.226.0/19'},
	     '192.168.1.23': {'ge-0/0/1':'72.114.255.3/19', 'ge-0/0/2':'72.114.194.0/19', 'ge-0/0/3':'72.114.255.34/19'} }

neighbor_info = {}
info_dict = {}
#topo_list = []
router_list = []
info_dict_list=[]

#function to create topology graph
def make_topo(info_dict_list, ip):
	#seperating nodes and edges from the dictionary
	device_list=[]							
	for device in info_dict_list:
		nodes = [device['nodes']]				#List of nodes - local devices
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
	#print(nodes)
	#print(edges)
	
	#graph creation
	dot= Graph(comment = "My Network Topology" , format = 'png', strict = True)	#Graph in png format; Strict = True to merge repeated interfaces
	dot.graph_attr['splines'] = 'ortho'
	for i in nodes:
		dot.node(i, shape = 'oval')
	for i in edges:
		dot.edge(i[0], i[1], headlabel=i[2], taillabel=i[3], fontsize = '10' )	#i[0] - local device; i[1] - remote device connected; i[2] - interface of the local device; i[3] = interface of the remote device.	
	return dot
	

try:
	for i,j in zip(host_ip, range(len(host_ip))):
		print(i, j)
		#Establish NETCONF session on the device
		device = Device(host=i, user='labuser', password='Labuser', normalize=True)	#device/user authentication prior to start of NETCONF session
		device.open()						#Open the device to start the NETCONF session
		device.bind(conf=Config)				#Bind the Config instance to the device
		var_dict = {'if_config': if_config[i] }
		device.conf.load(template_path='template_lldp.conf', template_vars = var_dict, merge = True)	#Load the config-Jinja template + python datastructure 
		success = device.conf.commit()				#changing the active configuration
		print("Success : {}".format(success))
		test = device.rpc.get_lldp_neighbors_information()	#rpc to get lldp neighbor information for Device i
		test1 = device.rpc.get_config()				#rpc to local host name
		info = test.findall("lldp-neighbor-information")
		local_router = test1.findall("system")
		for router in local_router:
			router_list.append(router[0].text)		#router list containing the names of the devices in the topology
			neighbor_info_list = []				#list containing the device's remote host name and interfaces
			for info1 in info:
				neighbor_info={"Local interface" : info1[0].text, "Remote host name" : info1[5].text, "Remote host interface" : info1[4].text}
				neighbor_info_list.append(neighbor_info)	
			info_dict = {'nodes':router[0].text , 'neighbor': (neighbor_info_list)}
			info_dict_list.append(info_dict)		#master dictionary list with host names and their neighbors
	dot = make_topo(info_dict_list)					#calling the function to make graph topology
	#print(dot.source)
	dot.render(filename='MyNetworkTopology')			#Render the graph image


except (RpcError, ConnectError) as err:					#Catch RPC error or connection error Exceptions
	print("\nError: " + repr(err))

finally:
	device.close()							#close device 
