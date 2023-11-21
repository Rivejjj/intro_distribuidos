from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr
#from collections import namedtuple
import json
import os

IPV4 = 0x800
IPV6 = 0x86dd
TCP = 6
UDP = 17

log = core.getLogger()

rules = []
firewall_dpid = None

class FirewallRule():
    def __init__(self, ip_protocol, src_ip, dst_ip, transport_protocol, src_port, dst_port):
        self.dst_ip = dst_ip
        self.src_ip = src_ip
        if src_ip != None:
            self.src_ip = IPAddr(src_ip)
        if dst_ip != None:
            self.dst_ip = IPAddr(dst_ip)

        self.src_port = src_port
        self.dst_port = dst_port
        if ip_protocol == "IPV4" or ip_protocol == IPV4:
            self.ip_protocol = IPV4
        elif ip_protocol == "IPV6" or ip_protocol == IPV6:
            self.ip_protocol = IPV6
        else:
            self.ip_protocol = None
        if transport_protocol == "UDP" or transport_protocol == UDP:
            self.transport_protocol = UDP
        elif transport_protocol == "TCP" or transport_protocol == TCP:
            self.transport_protocol = TCP
        else:
            self.transport_protocol = None
    
    def __str__(self):
        return f"ip_protocol = {self.ip_protocol} src_ip = {self.src_ip},dst_ip = {self.dst_ip}, src_port = {self.src_port}, dst_port = {self.dst_port}, transport_protocol = {self.transport_protocol} \n"
    
    def add_to_rules(self):
        if (self.src_port != None or self.dst_port != None) and self.transport_protocol == None:
            rule1 = FirewallRule(self.ip_protocol, self.src_ip, self.dst_ip, "UDP", self.src_port, self.dst_port)
            rule2 = FirewallRule(self.ip_protocol, self.src_ip, self.dst_ip, "TCP", self.src_port, self.dst_port)
            rule1.add_to_rules()
            rule2.add_to_rules()
        elif (self.src_ip != None or self.dst_ip != None or self.transport_protocol != None) and self.ip_protocol == None:
            rule1 = FirewallRule("IPV4",self.src_ip, self.dst_ip, self.transport_protocol, self.src_port, self.dst_port)
            rule2 = FirewallRule("IPV6",self.src_ip, self.dst_ip, self.transport_protocol, self.src_port, self.dst_port)
            rule1.add_to_rules()
            rule2.add_to_rules()
        else:
            rules.append(self)
    

class Firewall (EventMixin):
    
    def _load_rules_from_file(self, file_path):
        global firewall_dpid 
        try:
            with open(file_path, 'r') as file:
                read_rules = json.load(file)
                for rule in read_rules.values():
                    if firewall_dpid == None:
                        firewall_dpid = rule
                    else:
                        created_rule = FirewallRule(
                        rule.get("ip_protocol"),
                        rule.get("src_host"),
                        rule.get("dst_host"),
                        rule.get("transport_protocol"),
                        rule.get("src_port"),
                        rule.get("dst_port"))
                        created_rule.add_to_rules()
                    
        except FileNotFoundError:
            log.error(f"Error processing file: {file_path}")
            raise

    def __init__(self, rules_file_path):
        self.listenTo(core.openflow)
        self._load_rules_from_file(rules_file_path)
        log.debug(f"{rules}")
        for rule in rules:
            log.debug(f"{rule}")
        log.debug("Enabling Firewall Module")
        

    def _handle_ConnectionUp (self, event):
        if int(event.dpid) == firewall_dpid:
            log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))
            for rule in rules:
                self.add_firewall_rule(event.connection, rule)
        
    def add_firewall_rule(self, connection, rule):
        msg = of.ofp_flow_mod()
        msg.match.dl_type = rule.ip_protocol
        msg.match.nw_src = rule.src_ip
        msg.match.nw_dst = rule. dst_ip
        msg.match.nw_proto = rule.transport_protocol
        msg.match.tp_src = rule.src_port
        msg.match.tp_dst = rule.dst_port
        msg.hard_timeout = 0
        connection.send(msg)


def launch (rule="rule.json"):
    
    core.registerNew(Firewall, rule)
