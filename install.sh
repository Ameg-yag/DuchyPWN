# written by Jan "Duchy" Neduchal
# 2018
# Licenced under the MIT licence
if (( $EUID != 0 )); then
    fail "Script must be run as root"
    exit
fi

echo "Updating apt..."
apt-get update >/dev/null 2>&1

echo "Getting all dependencies..."
apt-get -y install libssl1.0-dev
apt-get -y install libnl-3-dev libnl-genl-3-dev
apt-get -y install python
apt-get -y install tcpdump
apt-get -y install git

echo "Getting pip..."
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
rm get-pip.py

python -m pip install netifaces
python -m pip install python-nmap

echo "Setting up scapy..."
git clone https://github.com/secdev/scapy/
python scapy/setup.py install
rm -rf scapy/

echo "All done!!"
