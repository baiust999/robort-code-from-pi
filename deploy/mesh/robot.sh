#!/bin/sh
# UCI provisioning for the Robot Mesh Router, Section 8.14.5.1.
#
# This is the mesh gateway: static mesh IP 192.168.10.1, Ethernet-connected
# to the Pi at 192.168.10.10, and the DHCP server for the mesh subnet. Run
# on the OpenWrt router physically attached to the robot chassis.
set -e

MESH_ID="robot-mesh"
MESH_KEY="RobotMesh2026!"
MESH_IP="192.168.10.1"

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

# Ethernet link to the Pi; this router is the Pi's default gateway.
uci set network.lan.ipaddr="$MESH_IP"
uci set network.lan.gateway="$MESH_IP"

uci set firewall.@forwarding[0].dest='mesh'

uci commit network
uci commit wireless
uci commit firewall

wifi reload
/etc/init.d/network restart
