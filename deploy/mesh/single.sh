#!/bin/sh
# UCI provisioning for a single-router deployment (no mesh).
#
# One OpenWrt router on the robot chassis does everything: LAN IP
# 192.168.10.1 (the Pi's gateway, MESH_GATEWAY in p3.env), Ethernet to the
# Pi at 192.168.10.10, and the operator access point "robot-mesh-ap" with
# DHCP 192.168.10.50-99. The operator laptop joins the AP directly, so range
# is one Wi-Fi hop. Use robot.sh/relay1.sh/relay2.sh instead once relay
# routers are available.
#
# Changing the LAN IP drops an SSH session on the old address; reconnect at
# 192.168.10.1 after the router restarts its network.
set -e

ROUTER_IP="192.168.10.1"
AP_SSID="robot-mesh-ap"
AP_KEY="OperatorAccess2026!"
COUNTRY="US"
CHANNEL="6"

uci set network.lan.ipaddr="$ROUTER_IP"
uci set network.lan.netmask='255.255.255.0'

uci set wireless.radio0.disabled='0'
uci set wireless.radio0.country="$COUNTRY"
uci set wireless.radio0.channel="$CHANNEL"
uci set wireless.radio0.htmode='HT20'

uci set wireless.default_radio0.mode='ap'
uci set wireless.default_radio0.network='lan'
uci set wireless.default_radio0.ssid="$AP_SSID"
uci set wireless.default_radio0.encryption='psk2'
uci set wireless.default_radio0.key="$AP_KEY"
uci set wireless.default_radio0.disabled='0'

uci set dhcp.lan.start='50'
uci set dhcp.lan.limit='50'

uci commit network
uci commit wireless
uci commit dhcp

wifi reload
/etc/init.d/dnsmasq restart
/etc/init.d/network restart
