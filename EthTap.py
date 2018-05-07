import gen_utils as gu
from arp import Arp_poison
from beacon import Beacon
import time
from os.path import dirname, basename, isfile
import glob
gu.root_check()

modules = glob("modules/*.py")  # loads all modules
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

def logo():
    print """______            _          ______ _    _ _   _
|  _  \          | |         | ___ \ |  | | \ | |
| | | |_   _  ___| |__  _   _| |_/ / |  | |  \| |
| | | | | | |/ __| '_ \| | | |  __/| |/\| | . ` |
| |/ /| |_| | (__| | | | |_| | |   \  /\  / |\  |
|___/  \__,_|\___|_| |_|\__, \_|    \/  \/\_| \_/
                         __/ |
                        |___/

            by Jan 'Duchy' Neduchal 2018"""

def menu():
    logo()
    print ""


def main():
    try:
        arp_attack = Arp_poison(gu.get_pub_ip(), gu.get_default_gateway())
    except invalidIface:
        print "The interface is invalid! (switch it to monitor mode)"
        sys.exit(1)

    try:
        mybeacon = Beacon() # enter a monitor iface here
    except invalidIface:
        print "The interface is invalid! (switch it to monitor mode)"
        sys.exit(1)

    mybeacon.send(ssid="TEST", enc = True)
    mybeacon.send(ssid="TEST1", enc = False)
    mybeacon.send(ssid="TEST2", enc = True)
    mybeacon.send(ssid="TEST3")
    mybeacon.list()
    mybeacon.stop()
    mybeacon.list()
    time.sleep(5)
    mybeacon.stop_all()
    arp_attack.poison_arp_table()
    time.sleep(10)
    arp_attack.restore_arp_table()

try:
    main()
except KeyboadInterrupt:
    print("Exitting")
