# Copyright 2011-2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
First iimplementation of the ARP_NAT functionality
"""

from pox.core import core
import pox

import pox.openflow.libopenflow_01 as of
from collections import defaultdict
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.util import str_to_bool
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
from pox.openflow.discovery import Discovery

from pox.lib.revent import *
import time
import socket

log = core.getLogger()

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0
arpNat = {}

class LearningSwitch (object):
  """
  The learning switch "brain" associated with a single OpenFlow switch.

  When we see a packet, we'd like to output it on a port which will
  eventually lead to the destination.  To accomplish this, we build a
  table that maps addresses to ports.

  We populate the table by observing traffic.  When we see a packet
  from some source coming from some port, we know that source is out
  that port.

  When we want to forward traffic, we look up the desintation in our
  table.  If we don't know the port, we simply send the message out
  all ports except the one it came in on.  (In the presence of loops,
  this is bad!).

  In short, our algorithm looks like this:

  For each packet from the switch:
  1) Use source address and switch port to update address/port table
  2) Is transparent = False and either Ethertype is LLDP or the packet's
     destination address is a Bridge Filtered address?
     Yes:
        2a) Drop packet -- don't forward link-local traffic (LLDP, 802.1x)
            DONE
        2b) - IF THE PACKET IS AN ARP REQ, SEND IT TO CONTROLLER, CHANGE
            SPA/SHA AND REROUTE IT AND ACT AS NAT
	    - IF THE PACKET IS ARP REP, LOOK IN THE TABLE AND CHECK IF A REQ IS PENDING
	      IF IT IS, SWITCH THE COMPONENTS. IF NOT, DROP (?)
  3) Is destination multicast?
     Yes:
        3a) Flood the packet
            DONE
  4) Port for destination address in our address/port table?
     No:
        4a) Flood the packet
            DONE
  5) Is output port the same as input port?
     Yes:
        5a) Drop packet and similar ones for a while
  6) Install flow table entry in the switch so that this
     flow goes out the appopriate port
     6a) Send the packet out appropriate port
  """
  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent
    self.ip = IPAddr("10.0.0.11")
    self.mac = EthAddr("00:11:22:33:44:55")
    # Our tables
    self.macToPort = {}
    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)


    # We just use this to know when to log a helpful message
    self.hold_down_expired = _flood_delay == 0

    # log.debug("Initializing LearningSwitch, transparent=%s",
    #          str(self.transparent))<F2>

  def _handle_PacketIn (self, event):
    """
    Handle packet in messages from the switch to implement above algorithm.
    """

    packet = event.parsed
    dpid = event.connection.dpid
    inport = event.port

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

    def drop_arp ():
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 10
        msg.hard_timeout = 10
        msg.buffed_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    self.macToPort[packet.src] = event.port # 1
    #print "self.src = " + self.src
    #print "self.hwsrc = " + self.hwsrc
    match = of.ofp_match.from_packet(packet)
    if not self.transparent: # 2
      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
        drop() # 2a
        return
    
    if match.dl_type == packet.ARP_TYPE:
        #drop_arp()
        ### do we have an ARP table in the controller as well?

        if match.nw_proto == arp.REQUEST:
            
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
                    #msg = of.ofp_packet_out()
                    #msg.match = of.ofp_match.from_packet(packet,event.port)
                    #msg.idle_timeout = 10
                    #msg.hard_timeout = 30
                    #msg.actions.append(of.ofp_action_output(port = self.macToPort[packet.dst]))
                    #msg.data = event.ofp
                    #self.connection.send(msg)
        return
    
    if packet.dst.is_multicast:
      flood() # 3a
    else:
      if packet.dst not in self.macToPort: # 4
        flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
      else:
        port = self.macToPort[packet.dst]
        if port == event.port: # 5
          # 5a
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          drop(10)
          return
        # 6
        log.debug("installing flow for %s.%i -> %s.%i" %
                  (packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp # 6a
        self.connection.send(msg)
    

class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__(self, transparent, ignore = None):
    """
    Initialize

    See LearningSwitch for meaning of 'transparent'
    'ignore' is an optional list/set of DPIDs to ignore
    """
    core.openflow.addListeners(self)
    self.transparent = transparent
    self.ignore = set(ignore) if ignore else ()

  def _handle_ConnectionUp (self, event):
    if event.dpid in self.ignore:
      log.debug("Ignoring connection %s" % (event.connection,))
      return
    log.debug("Connection %s" % (event.connection,))
    LearningSwitch(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay, ignore = None):
  """
  Starts an L2 learning switch.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  if ignore:
    ignore = ignore.replace(',', ' ').split()
    ignore = set(str_to_dpid(dpid) for dpid in ignore)

  core.registerNew(l2_learning, str_to_bool(transparent), ignore)
