# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do whatever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code

import nmap
import os
import sys
import gen_utils as gu
import requests # get()
import re
import socket # for dns resolution

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
        if self.log:
            with open(self.logfile, "a") as f:
                f.write("NMAP - scan_lan(ports=" + str(ports) + ")\n")
        if ports:
            args = "-F"
        else:
            args = "-sn"
        obj = nmap.PortScanner()
        range = gu.get_lan_range(self.iface)
        print "Scanning in range: " + range
        print "It may take a while.."
        obj.scan(hosts=range, arguments=args)
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
            if self.log:
                with open(self.logfile, "a") as f:
                    f.write("NMAP - scan_lan() results:\n")
                    f.write(obj.csv())


    def scan(self, ip, args = "-F -O", save = False, filename = ""):
        if self.log:
            with open(self.logfile, "a") as f:
                f.write("NMAP - scan(args=" + str(args) + ")\n")
        ipregex = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        domain = ""
        if not ipregex.match(ip):
            domain = re.sub('^(http|https)://', "",ip).replace("/", "")
            filename = domain + ".log"
            ip = socket.gethostbyname(domain)
        else:
            filename = str(ip)+".log"
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
                print "OS: " + str(obj[str(ip)]["osmatch"][0]["osclass"][0]["osfamily"]) + " " + obj[str(ip)]["osmatch"][0]["osclass"][0]["osgen"]
                print "\tOpen tcp ports: " + str(obj[ip].all_tcp())[1:][:-1]
                print "\tOpen udp ports: " + str(obj[ip].all_udp())[1:][:-1]
                print "\tOpen sctp ports: " + str(obj[ip].all_sctp())[1:][:-1]
                print "\tOpen ip ports: " + str(obj[ip].all_ip())[1:][:-1]
                if self.log:
                    with open(self.logfile, "a") as f:
                        f.write("NMAP - scan results:\n")
                        f.write(obj.csv())
                if 80 in obj[ip].all_tcp():
                    if domain != "":
                        url = "http://" + str(domain) + "/wp-admin"
                    else:
                        url = "http://" + str(ip) + "/wp-admin"
                    try:
                        req = requests.get(url, timeout=5)
                        if req.status_code == 200:
                            wordpress = re.findall('ver=.\..\..|ver=.\..', req.text)[0][4:]
                            print ""
                            print "Wordpress " + str(wordpress)
                            if self.log:
                                with open(self.logfile, "a") as f:
                                    f.write("Wordpress " + str(wordpress) + "\n")
                    except:
                        print "WordPress check timed out"
                    if domain != "":
                        url = "http://" + str(domain) + "/robots.txt"
                    else:
                        url = "http://" + str(ip) + "/robots.txt"
                    try:
                        req = requests.get(url, timeout=5)
                        if req.status_code == 200:
                            content = req.text.replace("\n", " ")
                            print ""
                            print "robots.txt: " + str(content)
                            if self.log:
                                with open(self.logfile, "a") as f:
                                    f.write("robots.txt: " + content)
                    except:
                        print "robots.txt check timed out"
