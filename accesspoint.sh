#!/bin/bash

sudo apt install hostapd -y
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo apt install dnsmasq -y
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

sudo service dhcpcd start
sudo systemctl enable dhcpcd
sudo iptables -t nat -A POSTROUTING -o usb0 -j MASQUERADE
sudo rfkill unblock wlan

DHCPCD_CONF="
hostname
clientid
persistent
option rapid_commit
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
option interface_mtu
require dhcp_server_identifier
slaac private

interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
"
echo "$DHCPCD_CONF" | sudo tee /etc/dhcpcd.conf > /dev/null

ROUTEDAP_CONF="
# https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
# Enable IPv4 routing
net.ipv4.ip_forward=1
"
echo "$ROUTEDAP_CONF" | sudo tee /etc/sysctl.d/routed-ap.conf > /dev/null

DNSMASQ_CONF="
interface=wlan0 # Listening interface
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
                # Pool of IP addresses served via DHCP
domain=wlan     # Local wireless DNS domain
address=/gw.wlan/192.168.4.1
                # Alias for this router
"
echo "$DNSMASQ_CONF" | sudo tee /etc/dnsmasq.conf > /dev/null


HOSTAPD_CONF="
country_code=SE
interface=wlan0
ssid=watertestriggobrr
hw_mode=g
channel=7
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=aesir2020
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"
echo "$HOSTAPD_CONF" | sudo tee /etc/hostapd/hostapd.conf > /dev/null

echo "Done"