# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do whatever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code
#
#
# You can contact me at honza.neduchal@gmail.com
import time
import glob  # for UNIX path resolution (folder/*)
import code
import sys
import readline
modules = glob.glob("modules/*.py") # load all modules to a var
modules_loaded = 0
modules_loaded_list = []
for f in modules:       # loads all from modules/
    if not f.endswith('__init__.py'):
        try:
            exec "from "+f[:-3].replace("/",".")+" import *"
            modules_loaded += 1
            modules_loaded_list.append(f[:-3].replace("modules/", ""))
        except Exception as err:
            print "Error in loading the module: " + f[:-3].replace("modules/", "")
            print "Error: " + str(err)
            print "Check module dependencies!"
            continue

root_check() # you need to run as root


def logo():
    os.system("clear")
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
    blank(1)
    print "Loaded " + str(modules_loaded) + " module(s)."
    blank(2)
    print "Type help for....you guessed it, HELP!"
    blank(9)

def print_help():
    print "Much of this shit depends on modules (see wiki for docs)"
    print"""some basic commands:
    help
    clear
    get_pub_ip()
    get_default_gateway()
    switch_to_monitor(iface = "The wireless interface")
    switch_to_managed(iface = "The wireless interface")
    list        (lists loaded modules)
    exit
    """

def main():
    menu()
    while 1:
        choice = raw_input("> ")
        if choice.lower() == "q" or choice.lower() == "exit" or choice.lower() == "quit":
            sys.exit(0)
        if choice.lower() == "help" or choice.lower() == "--help" or choice.lower() == "-h":
            print_help()
            continue
        if choice.lower() == "list" or choice.lower() == "lst":
            for x in range(len(modules_loaded_list)):
                print modules_loaded_list[x]
        if choice.lower() == "clear" or choice.lower() == "cls":
            menu()
            continue
        if choice.lower() == "info":
            try:
                print "Public IP: " + get_pub_ip()
            except:
                print "Not connected to the internet."
            try:
                print "Deafult Gateway: " + get_default_gateway()
            except:
                print "No default gateway found."
            list_ifaces()
            for x in range(len(modules_loaded_list)):
                print modules_loaded_list[x]
            continue

        try:
            exec choice    # execute inside the python interpreter (something like an interactive shell)
        except Exception as err:
            print str(err)
            print "Invalid command! Type help for....you guessed it, HELP!"
            continue

while 1:
    try:
        main()
    except KeyboardInterrupt:
        blank(1)
        if get_yn("Are you sure, you want to quit? (y/n):  "):
            print "Exitting"
            sys.exit(0)
        else:
            continue
