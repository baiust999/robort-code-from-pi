# Mesh Network Guide

How the robot's wireless network is built, how the software uses it, and how
to add another relay router.

**Sources this guide is based on:** `deploy/etc-robot/mesh.conf`,
`deploy/mesh/{robot,relay1,relay2,single}.sh`, `deploy/etc-robot/p{1,2,3}.env`,
`deploy/install.sh`, `pi/common/config.py`, `pi/p1_control/main.py`,
`pi/p2_media/signaling.py`, `dashboard/src/lib/{api,protocol}.ts`,
`dashboard/src/App.tsx`, and the mesh sections of
`docs/CAPSTONE_METHODOLOGY_FINAL.md` (Sections 10–13, 30, 38–40).

> **Section numbers:** the code comments cite "Section 8.9" and
> "Section 8.14.5.1". Those numbers come from an earlier version of the
> methodology. In the current `CAPSTONE_METHODOLOGY_FINAL.md` the mesh
> material is in **Sections 10–13** (configuration, HWMP, deployment, link
> quality) and **Section 38** (installation and field checklists).

---

## 1. Overview

### What the mesh is for

The operator drives the robot from a laptop browser. That laptop has to reach
the Raspberry Pi on the robot, which can be further away than one Wi-Fi hop
covers, often inside a damaged building. The mesh is a chain of OpenWrt
routers that carries that traffic:

```
operator laptop ──Wi-Fi──▶ Relay 1 ══mesh══ Relay 2 ══mesh══ Robot router ──Ethernet──▶ Pi
```

All control, telemetry, video, audio and the offline map travel over this
local network. Internet access is not needed. This is "Local Mesh Only"
mode, the only mode implemented: `ENABLE_OVERLAY=0` in `p3.env`.

### Why an 802.11s mesh

- **Range by adding hops.** Each relay extends coverage, so the operator can
  stay at a safe perimeter.
- **Self-forming.** Every node peers with every other node in radio range.
  The chain in the diagram is the *planned* layout, not fixed wiring
  (methodology §1.1).
- **Path re-selection.** 802.11s uses HWMP routing. If a link breaks and
  another path exists, traffic re-routes automatically (methodology §11.1,
  §33.1). If the broken relay was the only path, the link drops and the
  Arduino's 2 s dead-man stops the robot.
- **Layer-2 forwarding** (`mesh_fwding=1`): the whole mesh behaves as one
  Ethernet segment on a single `/24`, with no per-hop IP routing to configure.

### Two deployment modes

| Mode | Script(s) | When to use |
|---|---|---|
| **Full mesh** | `robot.sh` on the robot router, `relay1.sh` on the operator-side relay, `relay2.sh` on the interior relay | Normal deployment. Range is multi-hop. |
| **Single router** | `single.sh` on the robot router only | Bench testing, or when no relays are available. One router on the chassis provides the `robot-mesh-ap` access point and DHCP directly. There is no mesh. Range is one Wi-Fi hop. |

Both modes use the same addresses: the router at `192.168.10.1`, the Pi at
`192.168.10.10`, and laptops in `192.168.10.50–99`. The Pi and dashboard
config therefore does not change between modes.

---

## 2. Topology

```
                ┌──────────────────────────────────────┐
                │ OPERATOR LAPTOP                      │
                │ DHCP lease 192.168.10.50 – .99       │
                │ Browser → http://192.168.10.10:8080  │
                └──────────────────┬───────────────────┘
                                   │ Wi-Fi, SSID "robot-mesh-ap" (WPA2-PSK)
                ┌──────────────────▼───────────────────┐
                │ RELAY 1   192.168.10.2   relay1.sh   │
                │ mesh node + operator AP + DHCP       │
                └──────────────────┬───────────────────┘
                                   │ 802.11s mesh "robot-mesh" (SAE), ch 6 HT20
                ┌──────────────────▼───────────────────┐
                │ RELAY 2   192.168.10.3   relay2.sh   │
                │ pure mesh relay (no AP, no DHCP)     │
                └──────────────────┬───────────────────┘
                                   │ 802.11s mesh "robot-mesh" (SAE), ch 6 HT20
                ┌──────────────────▼───────────────────┐
                │ ROBOT ROUTER  192.168.10.1  robot.sh │
                │ on chassis, mesh gateway             │
                └──────────────────┬───────────────────┘
                                   │ Ethernet
                ┌──────────────────▼───────────────────┐
                │ RASPBERRY PI 4   192.168.10.10       │
                │ static IP, gateway 192.168.10.1      │
                │ P1 :8080   P2 :8443   P3 watchdog    │
                └──────────────────────────────────────┘
```

Single-router mode collapses this to: laptop ──Wi-Fi `robot-mesh-ap`──▶ robot
router `192.168.10.1` (single.sh) ──Ethernet──▶ Pi `192.168.10.10`.

> **Diagram inconsistency elsewhere:** `docs/high level software architure
> diagram.md` labels Relay 2 as `.2` and Relay 1 as `.3`, calls the SSID
> `robot-mesh`, and gives the DHCP pool as `.50-100`. The scripts and
> `mesh.conf` say Relay 1 = `.2`, Relay 2 = `.3`, AP SSID `robot-mesh-ap`
> (mesh ID `robot-mesh`), and pool `.50–.99`. **The scripts are
> authoritative.**

---

## 3. Addressing plan

From `deploy/etc-robot/mesh.conf`. No Pi process reads this file. It is the
reference that the router scripts and the Pi's static config must agree with.
`install.sh` copies it to `/etc/robot/mesh.conf`.

### Network-wide values

| Item | Value | Where it is set |
|---|---|---|
| Subnet | `192.168.10.0/24` (netmask `255.255.255.0`) | `mesh.conf` `MESH_SUBNET`; `network.mesh.netmask` in each script |
| Mesh ID | `robot-mesh` | `MESH_ID` in `robot.sh`, `relay1.sh`, `relay2.sh` |
| Operator AP SSID | `robot-mesh-ap` | `AP_SSID` in `relay1.sh` and `single.sh` |
| Operator DHCP range | `192.168.10.50` – `192.168.10.99` | `dhcp.lan.start='50'`, `dhcp.lan.limit='50'` in `relay1.sh` / `single.sh` |
| Default gateway for the Pi | `192.168.10.1` | `/etc/dhcpcd.conf` on the Pi (`install.sh` manual step 4); `MESH_GATEWAY` in `p3.env` |

### Nodes

| Node | Role | IP | Interface | Provisioned by |
|---|---|---|---|---|
| Robot router | Mesh node, gateway, Ethernet to the Pi | `192.168.10.1` | `network.mesh` (static) **and** `network.lan` (both set to `.1`) | `deploy/mesh/robot.sh` |
| Relay 1 | Mesh node + operator AP + DHCP | `192.168.10.2` | `network.mesh` (static); AP `wireless.ap` | `deploy/mesh/relay1.sh` |
| Relay 2 | Pure mesh relay | `192.168.10.3` | `network.mesh` (static) | `deploy/mesh/relay2.sh` |
| Raspberry Pi 4 | P1/P2/P3 | `192.168.10.10` | `eth0`, static | `install.sh` manual step 4 (`/etc/dhcpcd.conf`) |
| Operator laptop(s) | Dashboard | `.50` – `.99` | Wi-Fi client | DHCP from Relay 1 |
| *(single-router mode)* robot router | AP + DHCP, no mesh | `192.168.10.1` | `network.lan` | `deploy/mesh/single.sh` |

### Free addresses

| Range | Status |
|---|---|
| `.1` – `.3` | Routers (in use) |
| **`.4` – `.9`** | **Free. Use these for new relays.** |
| `.10` | Pi (in use) |
| `.11` – `.49` | Free (not allocated) |
| `.50` – `.99` | DHCP pool. **Never** assign statically. |
| `.100` – `.254` | Free (not allocated) |

---

## 4. Radio and mesh settings

All three mesh scripts set the same values. A node with a mismatched value
here **will not join the mesh**.

| Setting (UCI) | Value | What it does / why it matters |
|---|---|---|
| `wireless.radio0.channel` | `6` | 2.4 GHz channel 6. Every mesh node must be on the **same channel**, because a mesh point only peers on its own channel. 2.4 GHz was chosen for range and wall penetration over 5 GHz. |
| `wireless.radio0.htmode` | `HT20` | 20 MHz channel width. Narrower than HT40, which gives better range and less interference. About 1–2 Mbps is enough for one dashboard (methodology §39.2). Keep it identical on every node. |
| `wireless.mesh.mode` | `mesh` | Makes the wifi-iface an IEEE 802.11s mesh point. |
| `wireless.mesh.mesh_id` | `robot-mesh` | The mesh's "name". Nodes only peer with the same mesh ID. |
| `wireless.mesh.encryption` | `sae` | WPA3-SAE authentication and encryption between mesh peers. All nodes need the same key. Requires a full `wpad` build (see §7.1). |
| `wireless.mesh.key` | *(set via `MESH_KEY`)* | Shared mesh password. |
| `wireless.mesh.mesh_fwding` | `1` | Enables layer-2 multi-hop forwarding. Without it a node only talks to direct neighbours and **cannot relay**, which defeats the purpose of a relay. |
| `wireless.mesh.mesh_rssi_threshold` | `-80` | Peers weaker than −80 dBm are not accepted as mesh links. This stops a node from forming a marginal link that would carry traffic poorly. |
| `wireless.ap.mode` (Relay 1) | `ap` | Normal access point for operator laptops. |
| `wireless.ap.encryption` (Relay 1) | `psk2` | WPA2-Personal, so ordinary laptops can join. |
| Routing | HWMP (default) | Provided by the Linux mac80211 stack. The project doesn't configure it. Proactive root mode is **not** enabled (methodology §11.1). |
| Country code | `US` in `single.sh` only | The mesh scripts don't set `wireless.radio0.country`. TODO: verify the regulatory domain on each router (`iw reg get`) and set it to your country. |

### Passwords and keys

The real passwords are **not** reproduced here. They are plain-text variables
at the top of the scripts:

- **Mesh SAE key:** `MESH_KEY=` in `robot.sh`, `relay1.sh`, `relay2.sh` (must
  be identical in all of them).
- **Operator AP key:** `AP_KEY=` in `relay1.sh` and `single.sh`.

The committed values are defaults. **Change them before deployment** (the
methodology §10.1 and §38.1 say the same). Ideally, edit them on a local copy
of each script without committing the real keys to git. Anyone who has the AP
key can open the dashboard (methodology §40.3 item 6). The `CONTROLLER_KEY` in
`p1.env` is the only thing that stops them driving.

---

## 5. How the software uses the network

### Pi processes

| Process | Listens on | Protocol over the mesh | Notes |
|---|---|---|---|
| **P1** control server (`pi/p1_control`) | `0.0.0.0:8080` (`P1_HOST`/`P1_PORT`) | HTTP: dashboard static files at `/`, `/api/session`, `/api/ice-config`, `/api/gps-track`, `/maps/*` (offline map, HTTP range requests). WebSocket: `ws://192.168.10.10:8080/control/ws` for commands and the 200 ms telemetry stream. | Primary safety path. If the controller WebSocket drops, P1 sends `S` (stop). |
| **P2** media server (`pi/p2_media`) | `0.0.0.0:8443` (`P2_HOST`/`P2_PORT`) | HTTP `POST /webrtc/offer` (full SDP offer in, answer out, no trickle ICE). Then WebRTC media (SRTP/UDP) and the `screen` data channel directly between the laptop and the Pi. | Plain HTTP despite port 8443. The Robot Screen kiosk uses `localhost:8443` and never crosses the mesh. |
| **P3** watchdog (`pi/p3_watchdog`) | none | Health checks only, to `127.0.0.1:8080/health` and `127.0.0.1:8443/health` (localhost) | Reads `MESH_GATEWAY` (see below). |

**ICE / STUN.** `STUN_URL=stun:192.168.10.1:3478` in `p1.env` (P1 serves it
from `/api/ice-config`). Note:

- The dashboard currently creates `new RTCPeerConnection()` with **no** ICE
  servers (`dashboard/src/hooks/useWebrtcVideo.ts`), so it relies on host
  candidates only. That works because everything is on one `/24` with no NAT.
- None of the router scripts install a STUN server on `192.168.10.1`.
  TODO: verify whether anything should be listening on `:3478`. Today nothing
  depends on it.

### `MESH_GATEWAY`

`MESH_GATEWAY=192.168.10.1` in `deploy/etc-robot/p3.env` is loaded into
`P3Config.mesh_gateway` (`pi/common/config.py`). This is the only mesh value a
Pi process reads, and `mesh.conf` says the same. As of this writing, no code
after `config.py` uses `mesh_gateway`; P3 doesn't ping it or act on it.
TODO: verify whether a gateway reachability check was intended. The Pi's real
default route comes from `/etc/dhcpcd.conf` (`static routers=192.168.10.1`).

### Dashboard

- **Which host it talks to:** `dashboard/src/lib/api.ts` uses
  `VITE_ROBOT_HOST` if set, otherwise `window.location.hostname`. Because P1
  serves the dashboard, opening `http://192.168.10.10:8080` makes every
  request go to `192.168.10.10`: P1 on `:8080`, P2 on `:8443`
  (`VITE_P1_PORT` / `VITE_P2_PORT` override the ports).
- **Link status shown to the operator:**
  - `ConnectionStatusBar` shows **WS connected / WS offline**. The WebSocket
    reconnects with backoff from 1 s to 30 s and replays missed telemetry.
  - **Mission state** (`deriveMissionState` in `dashboard/src/lib/protocol.ts`,
    mirrored in `pi/common/protocol.py`): `STOP` if the WebSocket is down,
    serial is down, or there has been no telemetry for 3 s;
    `DRIVING_LIMITED` ("Video or mesh degraded — drive with caution") if
    WebRTC video is not connected **or** `meshOk` is false.
  - **`meshOk` is hard-coded to `true`** in `dashboard/src/App.tsx`. No
    process measures mesh signal or loss (methodology §40.3, known limitation
    1). A degrading mesh shows up only indirectly, as frozen video
    (`DRIVING_LIMITED`) or a dropped WebSocket (`STOP`).
- **Offline map:** `OfflineMapLayer.tsx` reads `area.pmtiles` from P1's
  `/maps/` over the mesh, so the map works with no internet. Map libraries load
  as a separate chunk so they don't slow the first page load over the mesh.

### Bandwidth budget (methodology §39.2, estimates)

One dashboard with VP8 video, robot audio, telemetry and the operator camera
uses about **1–2 Mbps**. Each extra viewing dashboard adds another video and
audio stream. Every relay hop shares the same channel-6 airtime, so effective
throughput roughly drops with each hop. Keep this in mind before adding many
relays (see §8).

---

## 6. Provisioning a router (existing roles)

### 6.1 Before you start

1. **Flash OpenWrt** on the router using the firmware and instructions for
   that model from the OpenWrt Table of Hardware. TODO: verify the router
   model(s) and OpenWrt version the team uses; neither is recorded in the
   repo.
2. **Make sure a full `wpad` package is installed** (needed for SAE mesh on
   `robot.sh`/`relay*.sh`, see §7.1). `single.sh` doesn't need it.
3. **Back up the current config** so you can roll back:
   ```sh
   sysupgrade -b /tmp/backup-$(cat /proc/sys/kernel/hostname).tar.gz
   # then copy it off the router, e.g. from the laptop:
   scp root@<router-ip>:/tmp/backup-*.tar.gz .
   ```
4. **Change the keys** (`MESH_KEY`, `AP_KEY`) in your local copy of the
   script (see §4).

### 6.2 Run the script

From a laptop wired to the router's LAN port (fresh OpenWrt is at
`192.168.1.1`):

```sh
# copy the right script (robot.sh, relay1.sh, relay2.sh or single.sh)
scp deploy/mesh/relay2.sh root@192.168.1.1:/tmp/
# On OpenWrt ≥ 22.03 scp may need -O (legacy protocol) if the router has no sftp-server.

ssh root@192.168.1.1
sh /tmp/relay2.sh
```

Each script runs with `set -e`, calls `uci commit` itself for `network`,
`wireless` and (where used) `dhcp`/`firewall`, and then runs `wifi reload`
and restarts networking. There is no separate commit step. **Reboot
afterwards** so the router comes up cleanly from the committed config:

```sh
reboot
```

Notes:
- `robot.sh` and `single.sh` change the LAN IP to `192.168.10.1`, so your SSH
  session drops. Reconnect at `192.168.10.1` (after giving your laptop an
  address in `192.168.10.0/24`).
- `relay1.sh` and `relay2.sh` do **not** change `network.lan`, so the LAN
  port stays at its previous address (OpenWrt default `192.168.1.1`).

### 6.3 Verify

On the router:

```sh
uci show wireless.mesh          # mode=mesh, mesh_id=robot-mesh, encryption=sae, ...
uci show network.mesh           # ipaddr 192.168.10.x
iw dev                          # find the mesh interface name (type "mesh point")
iw dev <mesh-iface> station dump   # one entry per mesh peer, with signal
iw dev <mesh-iface> mpath dump     # HWMP paths to other nodes
logread | grep -i -e mesh -e sae   # join / auth errors
```

From the operator laptop (joined to `robot-mesh-ap`):

```sh
ping -c 20 192.168.10.10    # target: < 5 % loss, < 200 ms (methodology §12.2)
```

Then run the field checklist in methodology §38.3.

### 6.4 Known gaps in the committed scripts — TODO: verify on hardware

While reading the scripts for this guide I found the following points. They
may be handled by manual steps nobody wrote down, or they may be real bugs.
**Check them on a real router before relying on the mesh path:**

1. **Mesh wifi-iface is not attached to a network.** All three mesh scripts
   create `network.mesh` (static IP) and `wireless.mesh` (mode `mesh`) but
   never set `wireless.mesh.network='mesh'`. Without that, the mesh radio
   interface is not bound to the `mesh` IP interface. Check `ip addr` on the
   router to see whether the `192.168.10.x` address actually appears.
2. **The operator AP on Relay 1 is not attached to a network either.**
   `wireless.ap` has no `network=` option. Laptops need to be bridged onto the
   same L2 segment as the mesh to reach `192.168.10.10`.
3. **Relay 1's DHCP pool is on `lan`, but its `lan` stays on the OpenWrt
   default subnet.** `relay1.sh` sets `dhcp.lan.start/limit` but never
   changes `network.lan.ipaddr`. With a default `lan` of `192.168.1.1`,
   laptops would get `192.168.1.50–99`, not `192.168.10.50–99`.
4. **Robot router has `.1` on two interfaces.** `robot.sh` sets both
   `network.mesh.ipaddr` and `network.lan.ipaddr` to `192.168.10.1` and sets
   `lan.gateway` to itself. On one `/24` this normally needs `mesh` and `lan`
   bridged into a single interface rather than two separate ones.
5. **Firewall zone `mesh` is not created.** `robot.sh` sets
   `firewall.@forwarding[0].dest='mesh'`, but no script defines a firewall
   zone named `mesh`.
6. **DHCP server location.** `SOFTWARE_ARCHITECTURE.md` and `ARCHITECTURE.md`
   say the robot router runs DHCP, but `robot.sh` configures no DHCP. Only
   `relay1.sh` and `single.sh` touch `dhcp.lan`. Two DHCP servers on one L2
   mesh would conflict, so decide which node owns DHCP.

`single.sh` doesn't have these problems: it uses the stock `lan` bridge with
the default AP attached. That is why single-router mode is the simplest
working setup.

---

## 7. How to add a new relay router (Relay 3)

The example adds **Relay 3 at `192.168.10.4`** as a pure relay, the same role
as Relay 2. Because the mesh is self-forming, Relay 3 needs no knowledge of
the other nodes. It only needs the same mesh ID, channel, width and key.

### 7.1 Hardware requirements

- **OpenWrt-supported router** with a **2.4 GHz** radio (`radio0` in the
  scripts must be the 2.4 GHz radio; check with `uci show wireless | grep band`
  or `iw list`). TODO: verify that `radio0` is 2.4 GHz on the specific model.
  On some dual-band routers it is the 5 GHz radio.
- **802.11s mesh support** in the driver. Check on the router:
  ```sh
  iw list | grep -A 12 "Supported interface modes" | grep -i "mesh point"
  ```
- **A full `wpad` build, not `wpad-basic`.** SAE (WPA3) on a mesh interface
  needs the mesh-capable variant. Replace the basic package:
  ```sh
  opkg update
  opkg remove wpad-basic-mbedtls wpad-basic-wolfssl wpad-basic 2>/dev/null
  opkg install wpad-mesh-openssl      # or wpad-openssl / wpad-mesh-wolfssl / wpad-wolfssl
  reboot
  ```
  Package names vary by OpenWrt release (OpenWrt 24.10+ uses `apk` instead of
  `opkg`). TODO: verify the exact package for the team's OpenWrt version. Do
  this **before** running the script, while the router still has internet
  access via its WAN port.
- **Power for the mission:** battery or mains, sized like the other relays
  (methodology §12.1).

### 7.2 Choose the IP

Rules:
- Not `.1`–`.3` (existing routers) and not `.10` (Pi).
- **Not in `.50`–`.99`**, the DHCP pool. A static address there can be handed
  to a laptop and cause an IP conflict.
- Keep relays together in the `.4`–`.9` block so the plan stays readable.

→ **Relay 3 = `192.168.10.4`.** Later relays: `.5`, `.6`, … up to `.9`.

### 7.3 Create `deploy/mesh/relay3.sh`

```sh
cp deploy/mesh/relay2.sh deploy/mesh/relay3.sh
```

Edit **only** these lines:

```diff
 #!/bin/sh
-# UCI provisioning for Relay Router 2, Section 8.14.5.1.
+# UCI provisioning for Relay Router 3, Section 8.14.5.1.
 #
-# Pure mesh relay: static mesh IP 192.168.10.3, no AP, no DHCP. Extends the
-# mesh fabric between the robot and Relay Router 1 when direct radio range
-# to the robot is insufficient from the operator's position.
+# Pure mesh relay: static mesh IP 192.168.10.4, no AP, no DHCP. Adds a
+# further hop to the mesh fabric where Relay 2 alone cannot reach the robot.
 set -e

 MESH_ID="robot-mesh"
 MESH_KEY="..."                       # unchanged: must match every other node
-MESH_IP="192.168.10.3"
+MESH_IP="192.168.10.4"
```

**Optional:** set a hostname so the node is easy to identify in `logread` and
LuCI. None of the existing scripts set one. If you add it, put it before the
`uci commit` lines:

```sh
uci set system.@system[0].hostname='relay3'
uci commit system
```

**Do not change** any of these. They must be identical on every mesh node:

| Must match | Value |
|---|---|
| `MESH_ID` | `robot-mesh` |
| `MESH_KEY` | same SAE key as all other nodes |
| `wireless.radio0.channel` | `6` |
| `wireless.radio0.htmode` | `HT20` |
| `wireless.mesh.encryption` | `sae` |
| `wireless.mesh.mesh_fwding` | `1` |
| `wireless.mesh.mesh_rssi_threshold` | `-80` |
| `network.mesh.netmask` | `255.255.255.0` |

Also do **not** copy the AP or DHCP blocks from `relay1.sh`. Only one node
should hand out `robot-mesh-ap` leases (see §6.4 item 6).

If you fix any of the gaps in §6.4 (e.g. adding `wireless.mesh.network`), make
the same fix in `relay3.sh` so all nodes stay consistent.

### 7.4 Update `deploy/etc-robot/mesh.conf`

Add the new entry under the existing relays:

```diff
 ROBOT_ROUTER_IP=192.168.10.1
 RELAY1_IP=192.168.10.2
 RELAY2_IP=192.168.10.3
+RELAY3_IP=192.168.10.4
 PI_STATIC_IP=192.168.10.10
```

No Pi process reads `mesh.conf`, so nothing needs restarting. On an
already-installed Pi, `install.sh` won't overwrite `/etc/robot/mesh.conf`.
Edit that copy by hand if you want it to stay in sync.

### 7.5 Update the other files that list the relays

See the full list in [Files to edit to add Relay 3](#files-to-edit-to-add-relay-3)
at the end. The minimum set is `relay3.sh`, `mesh.conf`, the `install.sh`
manual-step text ("three mesh routers"), `README.md` step 6, and the
methodology checklists in §38.

### 7.6 Provision the router

1. Flash OpenWrt and install the full `wpad` (§7.1).
2. Back up: `sysupgrade -b /tmp/backup-relay3.tar.gz` and copy it off.
3. Copy and run:
   ```sh
   scp deploy/mesh/relay3.sh root@192.168.1.1:/tmp/
   ssh root@192.168.1.1 'sh /tmp/relay3.sh && reboot'
   ```
   The `relay*.sh` scripts don't change `network.lan`, so after reboot you can
   still SSH in on the LAN port at its previous address.

### 7.7 Verify

Run these on **Relay 3** (`iw dev` tells you the mesh interface name, often
something like `mesh0` or `phy0-mesh0`; TODO: verify on your build):

```sh
iw dev                                   # interface of type "mesh point"
iw dev <mesh-iface> station dump         # should list its neighbours, signal ≥ about -70 dBm
iw dev <mesh-iface> mpath dump           # paths to other nodes' MAC addresses
ip addr                                  # 192.168.10.4 present?
ping -c 5 192.168.10.1                   # robot router
ping -c 5 192.168.10.10                  # Pi
```

Run these on **Relay 2 and the robot router** too. Relay 3 should now appear
in their `station dump` or `mpath dump`.

From the **operator laptop** (on `robot-mesh-ap`):

```sh
for ip in 1 2 3 4 10; do ping -c 5 -q 192.168.10.$ip; done
ping -c 20 192.168.10.10      # target < 5 % loss, < 200 ms
```

Then open `http://192.168.10.10:8080` and check (from methodology §38.3):

- [ ] Status bar shows **WS connected**, mission **READY**
- [ ] Video is live (no `DRIVING_LIMITED`)
- [ ] Drive briefly in each direction; the robot stops on release
- [ ] Hold **Talk**; your voice is heard from the robot speaker
- [ ] **Failover test (TEST_REPORT N8):** power off the middle relay while
      driving. The robot must stop within 2 s. If another path exists, the
      link should recover. Record the recovery time.

### 7.8 Where to place relays

From methodology §11.2, §12.1 and §13.1:

| RSSI per hop (from `station dump`) | Meaning |
|---|---|
| better than −65 dBm | Good |
| −65 to −75 dBm | Acceptable. The planning target is **better than −75 dBm** per hop. |
| −75 to −80 dBm | Poor. Expect video drops. |
| below −80 dBm | **No link.** Below `mesh_rssi_threshold`, so the nodes won't peer. |

Aim for about **−70 dBm or better** on every hop to leave margin before the
−80 cut-off.

- Place each relay where it has **line of sight** to both its neighbours
  (e.g. at a corridor junction or doorway), and **elevate** it: 1.5–2 m for
  the operator relay, 2–3 m for interior relays.
- Walk the relay toward the robot while watching `station dump`. Stop before
  the signal to the previous relay falls below about −70 dBm.
- Keep antennas clear of metal. On the robot, mount the router on top of the
  chassis.
- Power on in order: Relay 1, then the interior relays, then the robot
  (methodology §38.3).
- In a pure chain, every relay is a **single point of failure** (TEST_REPORT
  N8). If you have spare relays, overlapping coverage gives HWMP an alternate
  path.

---

## 8. Troubleshooting

| Symptom | Likely cause | Check / fix |
|---|---|---|
| **New node doesn't appear in any `station dump`** | Mesh ID, key, channel or HT mode differs; node too far away; wrong radio | `uci show wireless` on the new node and an existing one, then compare `mesh_id`, `key`, `channel`, `htmode`. Move the node closer. Confirm `radio0` is 2.4 GHz. `logread \| grep -i -e sae -e mesh` for auth failures. |
| **Wrong channel** | Router default or a manual change left it on another channel | `iw dev <mesh-iface> info` shows the current channel. Set `uci set wireless.radio0.channel='6'; uci commit wireless; wifi reload`. |
| **`wpad` missing / SAE fails** | `wpad-basic-*` installed: mesh interface fails to come up or SAE never completes | `opkg list-installed \| grep wpad` (or `apk list -I \| grep wpad`). Install the full or mesh variant (§7.1) and reboot. |
| **Mesh interface missing in `iw dev`** | Driver lacks mesh point mode, or the iface failed to start | `iw list` → "Supported interface modes" must include *mesh point*. `logread` for hostapd/wpad errors. |
| **IP conflict** (pings flap, "duplicate address") | Two nodes with the same `MESH_IP`, or a static IP inside `.50–.99` | `arping -I <iface> 192.168.10.x` from another node. Re-check §3 and the `MESH_IP` in each script. |
| **Peers visible, but ping to `192.168.10.x` fails** | The mesh iface isn't bound to the `mesh` IP interface (§6.4 items 1, 4) | `ip addr` on the node. Is `192.168.10.x` on the mesh interface or a bridge containing it? TODO: verify the intended bridge setup. |
| **Operator laptop gets no DHCP lease** | Not on `robot-mesh-ap`; AP not bound to a network; dnsmasq not running; pool exhausted (50 leases) | `logread \| grep dnsmasq` on Relay 1; `/etc/init.d/dnsmasq status`; check `wireless.ap.network`; check the lease file `/tmp/dhcp.leases`. |
| **Laptop gets a lease but in the wrong subnet** (e.g. `192.168.1.x`) | Relay 1's `lan` still on the OpenWrt default (§6.4 item 3) | `uci get network.lan.ipaddr` on Relay 1. |
| **Laptop gets two different leases / random gateways** | More than one DHCP server on the mesh segment | Make sure only one node runs DHCP for the mesh. Set `uci set dhcp.lan.ignore='1'` on the others (TODO: verify against your bridge setup). |
| **High latency or video drops over several hops** | Weak hop (< −75 dBm); airtime shared across hops on one channel; other 2.4 GHz traffic on channel 6 | `station dump` on each node, then find the weakest hop and move or elevate that relay. Remove a hop if possible. Scan for interference (`iw dev <iface> scan`, where the driver supports it). Close extra viewing dashboards; each one adds a video stream (§5). Dashboard: amber `DRIVING_LIMITED` then **Retry video**. |
| **Dashboard shows `WS offline` / STOP** | Control path lost (mesh partition, laptop out of range) | The dashboard reconnects automatically (1–30 s backoff). The robot has already stopped (dead-man). Move closer or add a relay. |
| **Page won't load** | Laptop not on the mesh, or the robot is still booting | Check you're on `robot-mesh-ap`. Wait 30 s. `ping 192.168.10.10`. |

### Rolling back a router

- **Restore the backup you made in §6.1:**
  ```sh
  scp backup-relay3.tar.gz root@<router-ip>:/tmp/
  ssh root@<router-ip> 'sysupgrade -r /tmp/backup-relay3.tar.gz && reboot'
  ```
- **Or factory-reset to stock OpenWrt** (erases all config; back at
  `192.168.1.1` after reboot):
  ```sh
  firstboot -y && reboot
  ```
- **Or take the node out of the mesh** without a reset:
  `uci set wireless.mesh.disabled='1'; uci commit wireless; wifi reload`.
- **Repo side:** delete `deploy/mesh/relay3.sh` and remove `RELAY3_IP` from
  `mesh.conf` (`git checkout -- <file>` if not yet committed).

Removing a relay doesn't need any change on the Pi or the other nodes. HWMP
drops paths through it on its own.

---

## 9. Quick reference: adding a relay

```
ADD A RELAY ROUTER — CHECKLIST

PLAN
  ☐ Pick a free IP in 192.168.10.4–.9   (not .1–.3, not .10, NOT .50–.99)
  ☐ Router is OpenWrt-supported, radio0 is 2.4 GHz, supports "mesh point"

PREPARE THE ROUTER
  ☐ Flash OpenWrt
  ☐ Replace wpad-basic with a full / mesh wpad, reboot
  ☐ sysupgrade -b backup, copy it off the router

REPO
  ☐ cp deploy/mesh/relay2.sh deploy/mesh/relayN.sh
  ☐ Change MESH_IP and the header comment (optional: hostname)
  ☐ Leave MESH_ID, MESH_KEY, channel 6, HT20, sae, mesh_fwding=1,
    mesh_rssi_threshold=-80 UNCHANGED
  ☐ Add RELAYN_IP to deploy/etc-robot/mesh.conf
  ☐ Update the docs / checklists that list the relays

PROVISION
  ☐ scp relayN.sh to the router; sh /tmp/relayN.sh; reboot

VERIFY
  ☐ iw dev                       → mesh point interface exists
  ☐ iw dev <if> station dump     → neighbours listed, ≥ about −70 dBm
  ☐ iw dev <if> mpath dump       → paths to the other nodes
  ☐ Other nodes see the new one in their station/mpath dump
  ☐ Laptop: ping .1 .2 .3 .N .10 → all answer
  ☐ ping -c 20 192.168.10.10     → < 5 % loss, < 200 ms
  ☐ Dashboard: WS connected, READY, live video, drive + stop, Talk works
  ☐ Power off a middle relay → robot stops ≤ 2 s; record recovery

PLACE
  ☐ Line of sight to both neighbours, elevated, antennas clear of metal
  ☐ Every hop better than −75 dBm (target about −70); −80 = no link
```

---

## Files to edit to add Relay 3

This guide only documents the change. Actually adding Relay 3 would touch
these files:

| File | Change |
|---|---|
| `deploy/mesh/relay3.sh` | **New**, copied from `relay2.sh` with `MESH_IP="192.168.10.4"` and an updated header |
| `deploy/etc-robot/mesh.conf` | Add `RELAY3_IP=192.168.10.4` |
| `deploy/install.sh` | Manual step 5: "the three mesh routers" → four, mention `relay3.sh` |
| `README.md` | Step 6 lists `robot.sh`, `relay1.sh`, `relay2.sh`; add `relay3.sh` |
| `docs/CAPSTONE_METHODOLOGY_FINAL.md` | §1.1 diagram, §1.2 ("3× OpenWrt routers"), §2/§3 subsystem tables ("3× OpenWrt"), §10.2 topology, §12 ("Three-Router Deployment"), §30.1 network path, §38.1 step 5, §38.2 mesh checklist, §38.3 power-up order, §39.1 hop list, dependency list ("MESH NETWORK (3 routers)") |
| `docs/SOFTWARE_ARCHITECTURE.md` | Tier 3 box ("3 x OpenWrt nodes"), the deployment sketch (".1 gateway / .2 relay+AP / .3 relay"), Figure A.9 address list, and the paragraph after it ("three OpenWrt nodes") |
| `docs/ARCHITECTURE.md` | Deployment flowchart `meshnet` subgraph: add a `.4 relay 3` node |
| `docs/high level software architure diagram.md` | `MESH` subgraph: add Relay 3 (and fix the swapped `.2`/`.3` labels while there) |
| `docs/OPERATOR_MANUAL.md` | Network checklist ("you → relay → relay → robot") if the standard chain becomes longer |
| `docs/TEST_REPORT.md` | Test setup table ("3 × OpenWrt"); add an "N3b — through 3 relays" row to the network tests |
| `docs/MESH.md` | This file: addressing table, topology diagram |
