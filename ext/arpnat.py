__author__ = 'ddurando'
"""
POX component - arpnat
The aim of this component is to address the problem of
ARP poisoning in SDN networks
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of

from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.revent import *
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
from collections import defaultdict
from pox.openflow.discovery import Discovery
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.recoco import Timer
import time

log = core.getLogger()
arpNat = {}
_flood_delay = 0

class ArpNat(object):
    def __init__(self):
        #self._expire_timer = Timer(5, _handle_expiration, recurring=True)
        self.ip = IPAddr("10.0.0.100")
        self.mac = EthAddr("00:11:22:33:44:55")
        core.addListeners(self)
        self.hold_down_expired = _flood_delay == 0

    def _handle_GoingUpEvent(self, event):
        core.openflow.addListeners(self)
        log.debug("up...")

    def _handle_ConnectionUp(self, event):
        fm1 = of.ofp_flow_mod()
        fm1.priority -= 0x1000
        fm1.match.dl_type = ethernet.ARP_TYPE
        fm1.match.nw_src = self.ip
        fm1.match.dl_src = self.mac
        fm1.match.nw_proto = arp.REQUEST
        fm1.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        fm1.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(fm1)

        fm2 = of.ofp_flow_mod()
        fm2.priority -= 0x1000
        fm2.match.dl_type = ethernet.ARP_TYPE
        fm2.match.nw_dst = self.ip
        fm2.match.dl_dst = self.mac
        fm2.match.nw_proto = arp.REPLY
        fm2.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        event.connection.send(fm2)


        fm3 = of.ofp_flow_mod()
        fm3.priority -= 0x1000
        fm3.match.dl_type = ethernet.ARP_TYPE
        fm3.match.nw_proto = arp.REQUEST
        fm3.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        event.connection.send(fm3)

        fm4 = of.ofp_flow_mod()
        fm4.priority -= 0x1000
        fm4.match.dl_type = ethernet.ARP_TYPE
        fm4.match.nw_proto = arp.REPLY
        fm4.actions.append(of.ofp_action_output(port=of.OFPP_NONE))
        event.connection.send(fm4)

    def _handle_PacketIn(self, event):
        dpid = event.dpid
        inport = event.port
        packet = event.parsed

        if not packet.parsed:
            log.warning("%s: ignoring unparsed packet", dpid_to_str(dpid))
            return

        def flood(message=None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            if time.time() - event.connection.connect_time >= _flood_delay:
                # Only flood if we've been connected for a little while...

                if self.hold_down_expired is False:
                    # Oh yes it is!
                    self.hold_down_expired = True
                    log.info("%s: Flood hold-down expired -- flooding",
                             dpid_to_str(event.dpid))

                if message is not None: log.debug(message)
                # log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
                # OFPP_FLOOD is optional; on some switches you may need to change
                # this to OFPP_ALL.
                msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            else:
                pass
                # log.info("Holding down flood for %s", dpid_to_str(event.dpid))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        def drop(duration=None):
            """
            Drops this packet and optionally installs a flow to continue
            dropping similar ones for a while
            """
            if duration is not None:
                if not isinstance(duration, tuple):
                    duration = (duration, duration)
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet)
                msg.idle_timeout = duration[0]
                msg.hard_timeout = duration[1]
                msg.buffer_id = event.ofp.buffer_id
                event.connection.send(msg)
            elif event.ofp.buffer_id is not None:
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                msg.in_port = event.port
                event.connection.send(msg)

        a = packet.find('arp')
        if not a: return

        log.debug("%s ARP %s %s => %s", dpid_to_str(dpid),
                  {arp.REQUEST: "request", arp.REPLY: "reply"}.get(a.opcode,
                                                                   'op:%i' % (a.opcode,)), str(a.protosrc),
                  str(a.protodst))

        if a.opcode == arp.REQUEST:

            if (packet.payload.hwsrc != self.mac and packet.payload.protosrc != self.ip):

                if (packet.payload.protodst in arpNat):
                    arpNat[packet.payload.protodst].append([packet.payload.hwsrc, packet.payload.protosrc, dpid, inport])

                else:
                    arpNat[packet.payload.protodst] = [[packet.payload.hwsrc, packet.payload.protosrc, dpid, inport]]

                r = arp()
                r.hwtype = r.HW_TYPE_ETHERNET
                r.prototype = r.PROTO_TYPE_IP
                r.hwlen = 6
                r.protolen = r.protolen
                r.opcode = r.REQUEST
                r.hwdst = ETHER_BROADCAST
                r.protodst = packet.payload.protodst
                r.protosrc = self.ip
                r.hwsrc = self.mac
                e = ethernet(type=ethernet.ARP_TYPE, src=self.mac, dst=ETHER_BROADCAST)
                e.payload = r

                tmpfm = of.ofp_flow_mod()
                tmpfm.priority -=0x1000
                tmpfm.match.dl_type = ethernet.ARP_TYPE
                tmpfm.match.nw_src = packet.payload.protosrc
                tmpfm.match.dl_src = packet.payload.hwsrc
                tmpfm.match.nw_proto = arp.REQUEST
                # tmpfm.actions.append(of.ofp_action_output(port=of.OFPP_NONE))
                for switch in core.openflow._connections.values():
                        switch.send(tmpfm)

                msg = of.ofp_packet_out()
                msg.data = e.pack()
                msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
                # msg.in_port = inport
                event.connection.send(msg)



            else:
                return

        elif a.opcode == arp.REPLY:
            if (arpNat[packet.payload.protosrc] and packet.payload.protodst == self.ip and packet.payload.hwdst == self.mac):
                drop()
                flag = False
                count = 0
                for e in arpNat[packet.payload.protosrc]:

                    if e[2] == dpid:
                        flag = True
                        i = count
                    count = count + 1
                if flag:

                    r = arp()
                    r.hwtype = r.HW_TYPE_ETHERNET
                    r.prototype = r.PROTO_TYPE_IP
                    r.hwlen = 6
                    r.protolen = r.protolen
                    r.opcode = r.REPLY
                    r.hwdst, r.protodst, outpid, outport = arpNat[packet.payload.protosrc].pop(i)
                    r.hwsrc = packet.payload.hwsrc
                    r.protosrc = packet.payload.protosrc
                    e = ethernet(type=ethernet.ARP_TYPE, src=self.mac, dst=r.hwdst)
                    e.set_payload(r)
                    log.debug("ARPing for %s on behalf of %s" % (r.protodst, r.protosrc))

                    tmpfm = of.ofp_flow_mod(command=of.OFPFC_DELETE)
                    tmpfm.priority -=0x1100
                    tmpfm.match.dl_type = ethernet.ARP_TYPE
                    tmpfm.match.nw_src = r.protodst
                    tmpfm.match.dl_src = r.hwdst
                    tmpfm.match.nw_proto = arp.REQUEST
                    for switch in core.openflow._connections.values():
                        switch.send(tmpfm)

                    msg = of.ofp_packet_out()
                    msg.data = e.pack()
                    msg.actions.append(of.ofp_action_output(port=outport))
                    msg.in_port = inport
                    event.connection.send(msg)
            else:
                return


def launch():
    log.info("arpNat component running")
    core.registerNew(ArpNat)