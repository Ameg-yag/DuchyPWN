def get_pub_ip():
    return urlopen('https://ip.42.pl/raw').read()


def get_default_gateway():
    return ni.gateways()['default'][ni.AF_INET][0]
