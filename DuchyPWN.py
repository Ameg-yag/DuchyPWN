# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
# Do what the f**k ever you want with the code, I don't really care. I <3 opensource.
# However note, that I, Jan Neduchal, take no responsibility for any malicious of your actions with this code
#
#
# You can contact me at honza.neduchal@gmail.com
import time
import glob
import readline
import code
modules = glob.glob("modules/*.py")
modules_loaded = 0
for f in modules:       # loads all from modules/
    if not f.endswith('__init__.py'):
        exec "from "+f[:-3].replace("/",".")+" import *"
        modules_loaded += 1


root_check()

def blank(n):
    for i in range (n):
        print ""

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
    switch_to_monitor(iface = "The goddamn wireless interface")
    exit"""

def main():
    menu()
    while 1:
        choice = raw_input("> ")
        if choice == "q" or choice == "exit" or choice == "quit":
            sys.exit(0)
        if choice == "help" or choice == "--help" or choice == "-h":
            print_help()
            continue
        if choice == "clear" or choice == "cls":
            menu()
            continue
        try:
            exec choice
        except:
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
