from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os



log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''




class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):
        ''' Add your logic here ... '''
        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))
        
        # Regla3: Impedir que se conecten 2 hosts
        # Esto se debe hacer dinamicamente, no estático
        h1 = EthAddr("00:00:00:00:00:01")
        h2 = EthAddr("00:00:00:00:00:02")
        self.add_firewall_rule(event.connection, h1, h2)
        self.add_firewall_rule(event.connection, h2, h1)
    

    def add_firewall_rule(self, connection, src_mac, dst_mac):
        # Agrega reglas para bloquear la comunicación entre src_mac y dst_mac
        msg = of.ofp_flow_mod()
        msg.match.dl_src = src_mac
        msg.match.dl_dst = dst_mac
        msg.hard_timeout = 0  # Permanente
        connection.send(msg)

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)



def get_host_by_name(topo, host_name):
    for node in topo.nodes():
        if node.name == host_name:
            return node
    return None