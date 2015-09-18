__author__ = 'ddurando'
"""
POX component - arpnat
The aim of this component is to address the problem of
ARP poisoning in SDN networks
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from collections import defaultdict
from pox.openflow.discovery import Discovery
from pox.lib.util import dpidToStr
from pox.lib.recoco import Timer
import time

log = core.getLogger()
arpNat = {}


class ArpNat(object):
    def __init__(self):
        self._expire_timer = Timer(5, _handle_expiration, recurring=True)

        core.addListeners(self)

    def _handle_GoingUpEvent(self, event):
        core.openflow.addListeners(self)
        log.debug("up...")

    def _handle_ConnectionUp(self, event):
        fm = of.ofp_flow_mod()
        fm.priority -= 0x1000
        fm.match.dl_type = ethernet.ARP_TYPE
        fm.actions.append(of.ofp_actions_output(port=of.OFPP_CONTROLLER))
        event.connection.send(fm)

    def _handle_PacketIn(self, event):
        dpid = event.dpid
        inport = event.port
        packet = event.parsed
        if not packet.parsed:
            log.warning("%s: ignoring unparsed packet", dpid_to_str(dpid))
            return
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            if time.time() - self.connection.connect_time >= _flood_delay:
            # Only flood if we've been connected for a little while...

                if self.hold_down_expired is False:
                    # Oh yes it is!
                    self.hold_down_expired = True
                    log.info("%s: Flood hold-down expired -- flooding",
                    dpid_to_str(event.dpid))

                if message is not None: log.debug(message)
                #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
                # OFPP_FLOOD is optional; on some switches you may need to change
                # this to OFPP_ALL.
                msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            else:
                pass
                #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
            msg.data = event.ofp
            msg.in_port = event.port
            self.connection.send(msg)

        def drop (duration = None):
        """
        Drops this packet and optionally installs a flow to continue
        dropping similar ones for a while
        """
            if duration is not None:
                if not isinstance(duration, tuple):
                    duration = (duration,duration)
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet)
                msg.idle_timeout = duration[0]
                msg.hard_timeout = duration[1]
                msg.buffer_id = event.ofp.buffer_id
                self.connection.send(msg)
            elif event.ofp.buffer_id is not None:
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                msg.in_port = event.port
                self.connection.send(msg)

        a = packet.find('arp')
        if not a: return

        log.debug("%s ARP %s %s => %s", dpid_to_str(dpid),
                  {arp.REQUEST: "request", arp.REPLY: "reply"}.get(a.opcode,
                  'op:%i' % (a.opcode,)), str(a.protosrc),
                  str(a.protodst))

        if a.nw_proto == arp.REQUEST:
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
                e = ethernet(type=ethernet.ARP_TYPE, src=self.mac,dst=ETHER_BROADCAST)
                e.payload = r
                log.debug("ARPing for %s on behalf of %s" % (r.protodst, r.protosrc))
                msg = of.ofp_packet_out()
                msg.data = e.pack()
                msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                # msg.in_port = inport
                event.connection.send(msg)
            else:
                flood()

        elif match.nw_proto == arp.REPLY:
            if (arpNat[packet.payload.protosrc] and packet.payload.protodst == self.ip and packet.payload.hwdst == self.mac):
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

                    msg = of.ofp_packet_out()
                    msg.data = e.pack()
                    msg.actions.append(of.ofp_action_output(port = outport))
                    msg.in_port = inport
                    event.connection.send(msg)
                else:
                    flood()
    def launch():
        core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
        log.info("arpNat component running")
