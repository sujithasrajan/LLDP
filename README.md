# LLDP

Python application that gathers network connectivity information and displays it on the screen in a graphical representation. In particular, the application 

• Enables and runs LLDP (Link-Layer Discovery Protocol)

• Gathers LLDP connectivity information from a set of pre-configured routers

• Displays the network graph on the screen including the routers and their connections. The routers are represented by a graphical icons, and the connections should be represented by lines connecting the icons. The interface numbers and Router name are displayed nearby the router and the corresponding connection line using Graphviz


1. workingLLDP.py    -> python code to be run
Command:  python3 workingLLDP.py

After completion, you can see the output graph image and layout command file in the directory.

2. template_lldp -> Jinja2 template file for configuration

3. MyNetworkTopology.png  -> Output graph image

4. MyNetworkTopology. -> Layout command file


![FLOW/STATE DIAGRAM](https://github.com/sujithasrajan/LLDP/blob/master/flow-diagram.png)
