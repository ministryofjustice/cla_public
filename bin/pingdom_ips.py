#!/usr/bin/env python3
import re
import requests
import sys


def get_pingdom_probe_ips():
    ip_list = []
    pingdom_link = "https://my.pingdom.com/probes/ipv4"
    pingdom_ips = requests.get(pingdom_link).text.split()
    parsed_pingdom_ip_list = ["".join([ip.strip(), "/32"]) for ip in pingdom_ips]
    regex = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/32$"

    for ip in parsed_pingdom_ip_list:
        if re.match(regex, ip) is not None:
            ip_list.append(ip)
    return ip_list


if __name__ == "__main__":
    ips = r"\,".join(get_pingdom_probe_ips())
    sys.stdout.write(ips)
