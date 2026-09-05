#!/bin/sh
# UCI provisioning for Relay Router 1, Section 8.14.5.1.
#
# Mesh relay plus the operator access point: static mesh IP 192.168.10.2,
# and an AP interface (SSID robot-mesh-ap) that the operator laptop joins,
# with DHCP handing out 192.168.10.50-99. This is the router the operator
# physically associates with.
set -e

MESH_ID="robot-mesh"
MESH_KEY="RobotMesh2026!"
MESH_IP="192.168.10.2"
AP_SSID="robot-mesh-ap"
AP_KEY="OperatorAccess2026!"

uci set network.mesh=interface
uci set network.mesh.proto='static'
uci set network.mesh.ipaddr="$MESH_IP"
uci set network.mesh.netmask='255.255.255.0'

uci set wireless.radio0.channel='6'
uci set wireless.radio0.htmode='HT20'

uci set wireless.mesh=wifi-iface
uci set wireless.mesh.device='radio0'
uci set wireless.mesh.mode='mesh'
uci set wireless.mesh.mesh_id="$MESH_ID"
uci set wireless.mesh.encryption='sae'
uci set wireless.mesh.key="$MESH_KEY"
uci set wireless.mesh.mesh_fwding='1'
uci set wireless.mesh.mesh_rssi_threshold='-80'

uci set wireless.ap=wifi-iface
uci set wireless.ap.device='radio0'
uci set wireless.ap.mode='ap'
uci set wireless.ap.ssid="$AP_SSID"
uci set wireless.ap.encryption='psk2'
uci set wireless.ap.key="$AP_KEY"

uci set dhcp.lan.start='50'
uci set dhcp.lan.limit='50'

uci commit network
uci commit wireless
uci commit dhcp

wifi reload
/etc/init.d/network restart
/etc/init.d/dnsmasq restart
