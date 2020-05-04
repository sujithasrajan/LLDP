from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import RpcError
from jnpr.junos.utils.config import Config
from lxml import etree as etree
from graphviz import Digraph

devices = {"192.168.1.21": "A", "192.168.1.22": "B", "192.168.1.23": "C", "192.168.1.24": "D"}
router_dict = {}

try:
    for local_host_ip, local_host_name in devices.items():
        device = Device(host=local_host_ip, user='labuser', password='Labuser', normalize=True)

        device.open()
        device.bind(conf=Config)
        test = device.rpc.get_lldp_neighbors_information(normalize=True)
        etree.dump(test)
        info = test.findall("lldp-neighbor-information")

        for info1 in info:
            router_dict[local_host_name] = {}

            router_dict[local_host_name].setdefault("Local_Interface_Name", [])
            router_dict[local_host_name].setdefault("Remote_Interface_Name", [])
            router_dict[local_host_name].setdefault("Remote_Host_Name", [])

        for info1 in info:
            router_dict[local_host_name]["Local_Interface_Name"].append(info1[0].text)  # Local Interface Name -
            router_dict[local_host_name]["Remote_Interface_Name"].append(info1[4].text)  # Remote Interface Name
            router_dict[local_host_name]["Remote_Host_Name"].append(info1[5].text)  # Remote Host Name


    dot = Graph(comment='Network Topology', strict=True)
    dot.attr('node', shape='circle')

    for i in list(router_dict.keys()):
        dot.node("i", i)

    for i in range(3):
        for j in range(3):
            dot.edge(list(router_dict.keys())[i], router_dict[list(router_dict.keys())[i]]["Remote_Host_Name"][j],
                     headlabel=router_dict[list(router_dict.keys())[i]]["Local_Interface_Name"][j],
                     taillabel=router_dict[list(router_dict.keys())[i]]["Remote_Interface_Name"][j])

    dot.view()


except (RpcError, ConnectError) as err:
    print("\nError: " + repr(err)

finally:
    device.close()



