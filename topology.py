from socket import timeout

# from sympy import hn1
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.node import Controller, RemoteController,OVSSwitch
import threading
import time
depth = 4
fanout = 2
hosts_num = 2**4
tree_topo = TreeTopo(depth=depth, fanout=fanout)
net = Mininet(topo=tree_topo, controller=RemoteController,switch=OVSSwitch)
net.start()

def ddos_flood(hosts, timeout, victim_host_ip):
    # Attack the last host with IP 10.0.0.4
    # timout command is used to abort the hping3 command after the attack was performed for the specifed time
    for host in hosts:
        # host.cmd('timeout ' + str(timeout) + 's hping3 --flood ' + ' -a '+ spoofed_ip +' '+ victim_host_ip)
        host.cmd('timeout ' + str(timeout) + 's hping3 --flood ' + victim_host_ip)
        host.cmd('killall hping3')


def ddos_benign(host, timeout, victim_host_ip):
    # Send benign packets to victim
    host.cmd('timeout ' + str(timeout) + 's hping3 ' + victim_host_ip)
    host.cmd('killall hping3')

h1 = net.get('h1')
h2 = net.get('h2')
hosts = []
for h in range(1,hosts_num+1):
    hosts.append(net.get('h'+str(h)))
attacker_hosts = hosts[4:]

normal_hosts = hosts[:4]

def start_normal_traffic(timeout):
    ddos_benign(normal_hosts[0],timeout,normal_hosts[1].IP())
    ddos_benign(normal_hosts[2],timeout,normal_hosts[0].IP())
    ddos_benign(normal_hosts[1],timeout,normal_hosts[3].IP())
    ddos_benign(normal_hosts[3],timeout,normal_hosts[0].IP())
    ddos_benign(normal_hosts[3],timeout,normal_hosts[2].IP())
    ddos_benign(normal_hosts[1],timeout,normal_hosts[0].IP())
    ddos_benign(normal_hosts[2],timeout,normal_hosts[3].IP())

t1 = threading.Thread(target=start_normal_traffic, args=(50,))
t2 = threading.Thread(target=ddos_flood, args=(attacker_hosts,30,h1.IP()))

t1.start()

time.sleep(50)
print("Starting attack")
t2.start()

t2.join()
t1.join()

net.stop() 