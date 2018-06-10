# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do whatever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code

import nmap
import os
import sys
import gen_utils as gu
import requests
import re

class Nmap:
    def __init__(self, iface = "eth0", DEBUG = False, log = False, logfile = "nmap.log"):
        self.iface = iface
        self.DEBUG = DEBUG
        try:
            self.pub_ip = gu.get_pub_ip()
        except:
            if self.DEBUG:
                print "Not connected to the internet!"
        self.log = log
        self.logfile = logfile
        if log:
            with open(self.logfile, "a") as f:
                f.write("Init NMAP\n")



    def __del__(self):
        if self.log:
            with open(self.logfile, "a") as f:
                f.write("Del NMAP\n")



    def scan_lan(self, ports = False):
        if ports:
            args = "-F"
        else:
            args = "-sn"
        obj = nmap.PortScanner()
        print "Scanning, it may take a while.."
        obj.scan(hosts=get_lan_range(self.iface), arguments=args)
        hosts = obj.all_hosts()
        print "\nHosts up: " + str(len(hosts))
        print ""
        for a in hosts:
            ports_open = []
            if ports:
                protocols = obj[a].all_protocols()
                for b in protocols:
                    for i in range(len(obj[a][b].keys())):
                        ports_open.append(obj[a][b].keys()[i])
            print "IP address: " + str(a)
            try:
                print "MAC address: " + str(obj[str(a)]["addresses"]["mac"]) + "  (" + str(obj[str(a)]["vendor"][obj[str(a)]["addresses"]["mac"]]) + ")"
            except:
                pass
            if ports:
                if len(ports_open) == 0:
                    print "\tOpen ports: None"
                else:
                    print "\tOpen ports: " + str(ports_open)[1:][:-1]
            print ""


    def scan(self, ip, args = "-F -O"):
        ipregex = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        if not ipregex.match(ip):
            domain = re.sub('^(http|https)://', "",ip).replace("/", "")
            ip = socket.gethostbyname(domain)
        obj = nmap.PortScanner()
        obj.scan(ip, arguments = args)
        if obj[ip].state() != "up":
            print "The host is DEAD"
            return
        else:
            print ""
            if args != "-F -O":
                print obj[ip].csv()
            else:
                if domain != "":
                    print "Domain: " + domain
                print "IP address: " + ip
                print "MAC address: " + "MAC address: " + str(obj[str(ip)]["addresses"]["mac"]) + "  (" + str(obj[str(ip)]["vendor"][obj[str(ip)]["addresses"]["mac"]]) + ")"
                print "OS: " + str(obj[str(ip)]["osmatch"][0]["osclass"][0]["osfamily"]) + " Version: " + obj[str(ip)]["osmatch"][0]["osclass"][0]["osgen"]
                print "\tOpen tcp ports: " + str(obj[ip].all_tcp())[1:][:-1]
                print "\tOpen udp ports: " + str(obj[ip].all_udp())[1:][:-1]
                print "\tOpen sctp ports: " + str(obj[ip].all_sctp())[1:][:-1]
                print "\tOpen ip ports: " + str(obj[ip].all_ip())[1:][:-1]
                print ""
                if "80" in obj[ip].all_tcp():
                    url = str(ip)+"/wp-admin"
                    req = requests.get(url)
                    if req.status_code == 200:
                        wordpress = re.findall('ver=.\..\..|ver=.\..', req.text)[4:]
                        print ""
                        print "Wordpress " + wordpress

                    url = str(ip)+"/robots.txt"
                    req = requests.get(url)
                    if req.status_code == 200:
                        content = req.text.replace("\n", " ")
                        print ""
                        print "robots.txt: " + content
