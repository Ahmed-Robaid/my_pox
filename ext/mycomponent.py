
from pox.core import core

from pox.lib.addresses import EthAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp

from pox.lib.recoco import Timer
from pox.lib.revent import Event, EventHalt

import pox.openflow.libopenflow_01 as of

import pox.openflow.discovery as discovery

from pox.lib.revent.revent import *

import time

import pox

class MyComponent(EventMixin):
    _eventMixin_events = set([newEvent,])


asd = MyComponent()
asd.addListenerByName("newEvent", _handle_newEvent)
