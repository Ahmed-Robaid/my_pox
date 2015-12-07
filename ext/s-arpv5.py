import sys, os, time
import datetime
from pox.core import core
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
from pox.lib.util import str_to_bool
import pox.openflow.libopenflow_01 as OpF
import pox.lib.packet as pkt

# Hosts IP <-> MAC table
hosts = {}

PRIORITY = 65535 // 2 


for i in range(1, 256):
    hosts["10.0.0." + str(i)] = "00:00:00:00:00:" + hex(i)[2:]

class SecureARP(object):
    def __init__(self, connection, transparent):
        self.macToPort = {}
        self.connection = connection
        self.transparent = transparent

        # for _handle_PacketIn to work
        core.addListeners(self, priority = PRIORITY)
        core.openflow.addListeners(self, priority = PRIORITY)
        connection.addListeners(self, priority = PRIORITY)

        # Rule for ARP
        default_timout = OpF.OFP_FLOW_PERMANENT
        msg = OpF.ofp_flow_mod()
        msg.match = OpF.ofp_match(dl_type = pkt.ethernet.ARP_TYPE)
        msg.idle_timeout = default_timout
        msg.hard_timeout = default_timout
        msg.priority = PRIORITY
        msg.actions.append(OpF.ofp_action_output(port = OpF.OFPP_CONTROLLER))
        self.connection.send(msg)
        
        
    def _handle_PacketIn(self, event):
        packet = event.parsed

        def drop():
            msg = OpF.ofp_flow_mod()
            msg.match = OpF.ofp_match.from_packet(packet)
            msg.idle_timeout = 1000
            msg.hard_timeout = 1000
            msg.priority = PRIORITY
            self.connection.send(msg)
        
        # ARP proccessing...
        if packet.type == packet.ARP_TYPE:
            src_mac_eth = packet.src
            dst_mac_eth = packet.dst
            src_ip_arp = packet.payload.protosrc
            src_mac_arp = packet.payload.hwsrc 
            dst_ip_arp = packet.payload.protodst
	# Checking our table...
            if EthAddr(hosts[str(src_ip_arp)]) != src_mac_arp:
                #print "Spoofing detected: IP and MAC not matched"
                #print '-> from', src_mac_arp
                drop()
                return
            '''   
            if src_mac_eth != src_mac_arp:
                print "Spoofing detected: source MAC and src MAC ARP mismatch"
                print '-> from', src_mac_arp
                drop()
                return
          
            if str(src_ip_arp) not in hosts.keys():
                self.log("WARN: new hosts entry: " + str(src_ip_arp) + " <-> " + str(src_mac_arp))
                print 'WARN: new hosts entry: ' + str(src_ip_arp) + ' <-> ' + str(src_mac_arp)
                hosts[str(src_ip_arp)] = str(src_mac_arp)
            
            
                
            # Check if the dst host is already in the network
            if dst_ip_arp not in hosts.keys():
                print "Spoofing detected: Dest host ip not in table"
                print '-> from', src_mac_arp
                drop()
                return
            
            # Else valid ARP packet
            self.log("OK, valid ARP")
            '''
class Controller(object):
    def __init__(self, transparent):
        core.openflow.addListeners(self, priority = PRIORITY)
        self.transparent = transparent
    def _handle_ConnectionUp(self, event):
        SecureARP(event.connection, self.transparent)

def launch(transparent = True, hold_down = 0):
    core.registerNew(Controller, str_to_bool(transparent))

