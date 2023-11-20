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
                self.rules_data = json.load(file).get("rules")
                log.debug(f"Loaded rules from {file_path}: {self.rules_data}")
            return self.rules_data
        except FileNotFoundError:
            log.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError:
            log.error(f"Error decoding JSON in file: {file_path}")
            raise


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
        self.apply_rule_1(event)
        
        # # Rule 2
        self.apply_rule_2(event)

        # Rule 3
        self.apply_rule_3(event)


    def apply_rule_1(self, event):
        """
        Apply the first rule: Discard all messages with destination port 80.

        Parameters:
        - event: OpenFlow event triggered when a switch connection is established.

        This function uses the add_firewall_rule function to add a rule to the switch
        that discards all messages with destination port 80.
        """
        rule_1 = self.rules_data.get("rule_1")
        dst_port = rule_1.get("dst_port")
        log.debug(f"Applying Rule 1: Discard messages with destination port {dst_port}")
        # Pregunta: Porque solo filtramos solo conexiones TCP?
        self.add_firewall_rule(event.connection, transport_protocol=TCP,dst_port=dst_port)
        log.debug("Rule 1 applied successfully.")


    def apply_rule_2(self, event):
        """
        Apply the second rule: Discard messages from host 1 with destination port 5001 and using UDP.

        Parameters:
        - event: OpenFlow event triggered when a switch connection is established.

        This function uses the add_firewall_rule function to add a rule to the switch
        that discards all messages from host 1 with destination port 5001 and using UDP.
        """
        rule_2 = self.rules_data.get("rule_2")
        str_ip = rule_2.get("src_host")
        h1 = IPAddr(str_ip)
        protocol = rule_2.get("protocol")
        dst_port = rule_2.get("dst_port")
        log.debug(f"Applying Rule 2: Discard messages from host {h1} with destination port {dst_port} and using UDP.")
        self.add_firewall_rule(event.connection, dst_ip=h1,transport_protocol=protocol,dst_port=dst_port)
        log.debug("Rule 2 applied successfully.")

    def apply_rule_3(self, event):
        """
        Apply the third rule: Prevent communication between two specified hosts.

        Parameters:
        - event: OpenFlow event triggered when a switch connection is established.

        This function uses the add_firewall_rule function to add rules to the switch
        that prevent communication between the specified hosts.
        """
        log.debug("Applying Rule 3: Prevent communication between two specified hosts.")
        rule_3 = self.rules_data.get("rule_3")
        str_ip = rule_3.get("src_host")
        h1 = IPAddr(str_ip)
        str_ip = rule_3.get("dst_host")
        h2 = IPAddr(str_ip)
        log.debug(f"Applying Rule 3: Prevent communication between {h1} and {h2}.")
        self.add_firewall_rule(event.connection, h1, h2)
        self.add_firewall_rule(event.connection, h2, h1)
        log.debug("Rule 3 applied successfully.")

    def add_firewall_rule(self, connection, src_ip=None, dst_ip=None, transport_protocol=None, src_port=None, dst_port=None):
        """
        Add a rule to the switch using an OpenFlow message to filter packets.

        Parameters:
        - connection: OpenFlow connection object to the switch.
        - src_ip: Source IP address for the rule (optional).
        - dst_ip: Destination IP address for the rule (optional).
        - transport_protocol: Transport protocol for the rule (optional).
        - src_port: Source port for the rule (optional).
        - dst_port: Destination port for the rule (optional).

        Note: Unspecified parameters are set to None.

        The function creates an OpenFlow message with the specified rule and sends it to the switch.
        """
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x800
        msg.match.nw_src = src_ip
        msg.match.nw_dst = dst_ip
        msg.match.nw_proto = transport_protocol
        msg.match.tp_src = src_port
        msg.match.tp_dst = dst_port
        msg.hard_timeout = 0  # Permanente
        connection.send(msg)


def launch (rule="rule.json"):
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall, rule)
