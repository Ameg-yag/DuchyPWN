# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do whatever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code

import netifaces as ni
import requests
import random
import os
import sys
import re

def get_lan_range(interface):
    iface_dict = ni.ifaddresses(interface)
    netmask = iface_dict[ni.AF_INET][0]["netmask"]
    addr = iface_dict[ni.AF_INET][0]["addr"]
    addr_lst = addr.split(".")
    if netmask == "255.255.255.0":
        return ("{0}.{1}.{2}.0/24".format(addr_lst[0], addr_lst[1], addr_lst[2]))
    if netmask == "255.255.0.0":
        return ("{0}.{1}.0.0/16".format(addr_lst[0], addr_lst[1]))
    if netmask == "255.0.0.0":
        return ("{0}.0.0.0/8".format(addr_lst[0]))

def get_pub_ip():
    return (requests.get('https://ip.42.pl/raw').text)


def get_default_gateway():
    return ni.gateways()['default'][ni.AF_INET][0]

def rand_mac():
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
        )

def root_check():
    if not os.geteuid() == 0:
        sys.exit("Not root! Run this with sudo..")

def switch_to_monitor(iface):
    if os.system("iwconfig %s| grep 'No wireless extensions' >/dev/null 2>&1" % iface) != 0:
        if os.system("iwconfig %s| grep 'Monitor' >/dev/null 2>&1" % iface) == 0:
            return iface
        else:
            os.system('ip link set %s down' % iface)
            os.system('iwconfig %s mode monitor' % iface)
            os.system('ip link set %s up' % iface)
            return iface
    else:
        raise Exception("invalidIface")

def switch_to_managed(iface):
    if os.system("iwconfig %s| grep 'No wireless extensions' >/dev/null 2>&1" % iface) != 0:
        if os.system("iwconfig %s| grep 'Monitor' >/dev/null 2>&1" % iface) != 0:
            return iface
        else:
            os.system('ip link set %s down' % iface)
            os.system('iwconfig %s mode managed' % iface)
            os.system('ip link set %s up' % iface)
            return iface
    else:
        raise Exception("invalidIface")


def get_yn(prompt):
    while True:
        try:
           return {"y":True,"n":False}[raw_input(prompt).lower()]
        except KeyError:
           print "\nInvalid input please enter y/n!"

def list_ifaces():
    ifaces = ni.interfaces()
    if len(ifaces) < 1:
        print "No interfaces found"
        return
    for i in range(len(ifaces)):
        if os.system("iwconfig " + ifaces[i] + "| grep Monitor >/dev/null 2>&1") != 0:
            if os.system("iwconfig " + ifaces[i] + "| grep wireless extensions >/dev/null 2>&1") == 0:
                print str(i+1) + ". " + ifaces[i] + " no wireless extension"
            else:
                print str(i+1) + ". " + ifaces[i] + " Managed mode"
        else:
            print str(i+1) + ". " + ifaces[i] + " Monitor mode"


def blank(n):
    for i in range (n):
        print ""
