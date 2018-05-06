import netifaces as ni
from urllib2 import urlopen
import random

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
