from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr
from collections import namedtuple
import json
import os


TCP = 6
UDP = 17
# IP_PROTO_ICMP: 1
# IP_PROTO_IGMP: 2
# IP_PROTO_GRE: 47
# IP_PROTO_OSPF: 89
# IP_PROTO_PIM: 103
# IP_PROTO_VRRP: 112
# IP_PROTO_SCTP: 132


log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''

hosts = {}


class Firewall (EventMixin):

    def __init__(self, rules_file_path):
        """
        Initializes the Firewall module.

        Parameters:
        - rules_file_path (str): The file path to the JSON file containing firewall rules.

        This method listens to OpenFlow events, loads firewall rules from the specified file,
        and enables the Firewall Module.

        Args:
        - rules_file_path (str): The file path to the JSON file containing firewall rules.
        """
        self.listenTo(core.openflow)
        self._load_rule_from_file(rules_file_path)
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):
        ''' Add your logic here ... '''
        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))
        

        # Rule 1
        # Pregunta: Porque solo filtramos solo conexiones TCP?
        self.add_firewall_rule(event.connection, transport_protocol=TCP,dst_port=80) 
        
        # Regla3: Impedir que se conecten 2 hosts
        # Esto se debe hacer dinamicamente, no estático
        h1 = IPAddr("10.0.0.1")
        h2 = IPAddr("10.0.0.2")
        self.add_firewall_rule(event.connection, h1, h2)
        self.add_firewall_rule(event.connection, h2, h1)

        # Rule 2
        self.add_firewall_rule(event.connection, dst_ip=h1,transport_protocol=UDP,dst_port=5001)


    def add_firewall_rule(self, connection, src_ip=None, dst_ip=None, transport_protocol=None, src_port=None, dst_port=None):
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x800
        msg.match.nw_src = src_ip
        msg.match.nw_dst = dst_ip
        msg.match.nw_proto = transport_protocol
        msg.match.tp_src = src_port
        msg.match.tp_dst = dst_port
        msg.hard_timeout = 0  # Permanente
        connection.send(msg)

def _load_rule_from_file(self, file_path):
    """
    Loads a firewall rule from a JSON file.

    Parameters:
    - file_path (str): The path to the JSON file containing the firewall rule.

    Raises:
    - FileNotFoundError: If the specified file_path does not exist.
    - json.JSONDecodeError: If there is an issue decoding the JSON content.

    Returns:
    - dict: The loaded firewall rule as a dictionary.
    """
    try:
        with open(file_path, 'r') as file:
            self.rule = json.load(file)
            log.debug(f"Loaded rule from {file_path}: {self.rule}")
        return self.rule
    except FileNotFoundError:
        log.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        log.error(f"Error decoding JSON in file: {file_path}")
        raise



#match = ofmatch.Match(
#    in_port=12, dl_src=None, dl_dst=None, dl_vlan=11423, dl_vlan_pcp=None,
#    dl_type=0x800, nw_tos=0, nw_proto=None, nw_src=None, nw_dst=None,
#   tp_src=None, tp_dst=None)

def launch (rule="rule.json"):
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall, rule)



def get_host_by_name(topo, host_name):
    for node in topo.nodes():
        if node.name == host_name:
            return node
    return None
