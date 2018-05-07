# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do whatever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code
import netifaces as ni
from urllib2 import urlopen
import random
import os
import sys

def get_pub_ip():
    return urlopen('https://ip.42.pl/raw').read()


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
