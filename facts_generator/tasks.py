# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from collections import OrderedDict
from nettoolkit import STR, Default

from .templates import iftype_templ, ParametersTemplate as para

# ---------------------------------------------------------------------------- #
# General Functions
# ---------------------------------------------------------------------------- #

def nested_col_values(dic):
	for headername, headervalues in dic.items():
		this_def_col_name = headername
		if isinstance(headervalues, (dict, OrderedDict)):
			yield nested_col_values(headervalues)
		elif isinstance(headervalues, (list, tuple)):
			yield (this_def_col_name, [headervalues, ])
		else:
			yield (this_def_col_name, headervalues)

def flat_dict(given_int_dictionary, int_type=None):
	d = {}
	if int_type: d['int_type'] = int_type
	for int_id, int_dict in given_int_dictionary.items():
		if isinstance(int_dict, (dict, OrderedDict)):
			for col_name_suffix, value in nested_col_values(int_dict):
				d[str(int_id)+"_"+col_name_suffix] = value
		else:
			d[int_id] = int_dict
	return d


def merge_vlan_intVlan(facts):
	intvlan_attribs = facts['vlans']
	for vlnumber, vlanattrib in intvlan_attribs.items():
		for intvl, intvlattr in facts['interfaces']['VLAN'].items():
			if vlnumber == intvlattr['int_number']:
				intvlattr.update(vlanattrib)
				break

# ---------------------------------------------------------------------------- #
# Common Tasks
# ---------------------------------------------------------------------------- #
class Tasks():

	number_of_max_extended_ips = 6		# e.g : starting from 0 - 5 = 6

	def __init__(self, run_list, lldp_list, int_status_list):
		self.run_list = run_list
		self.lldp_list = lldp_list
		self.int_status_list = int_status_list
		self.instance_var()
		self.facts = {"bgp":{},}

	def get_aaza(self):
		self.aaza()
		self.interface_aaza()
		self.lldp_aaza()
		self.get_facts_standard()
		# merge_vlan_intVlan(self.facts)

	def instance_var(self):
		############### OLD SETS ###############
		self.ifs, self.vrfs, self.vlans, self.vlan_member_names = [], [], [], []
		# self.vrfs, self.vlans, self.vlan_member_names = [], [], []
		self.ospf, self.bgp , self.routes = [], [], []
		self.bgp_af = []
		self.if_types = {
			"LOOPBACK": [], 
			"AGGREGATED": [], 
			"PHYSICAL": [], 
			"TUNNEL": [],
			"VLAN": [],
			"RANGE":[],
			"MANAGEMENT": [],
			}
		############### NEW SETS ###############
		self.ifloopbacks = {}
		self.ifaggregates = {}
		self.ifphysicals = {}
		self.iftunnels = {}
		self.ifvlans = {}
		self.ifranges = {}
		self.ifmanagement = {}
		self.instances = {'global':{}, }
		self.var = para.var()
		self.jfacts = {'var': self.var, 'instances': self.instances,
			'ifloopbacks': self.ifloopbacks , 'ifaggregates': self.ifaggregates, 
			'ifphysicals': self.ifphysicals, 'iftunnels': self.iftunnels, 'ifvlans': self.ifvlans,
			'ifranges': self.ifranges, 'ifmanagement': self.ifmanagement
		}
		self.iftype_ifvar = {
			"LOOPBACK": self.ifloopbacks, 
			"AGGREGATED": self.ifaggregates, 
			"PHYSICAL": self.ifphysicals, 
			"TUNNEL": self.iftunnels,
			"VLAN": self.ifvlans,
			"RANGE": self.ifranges,
			"MANAGEMENT": self.ifmanagement,
		}

	def get_facts_standard(self):
		self.get_facts_hostname()
		self.get_facts_interfaces()
		self.get_facts_vlans()
		if len(self.vrfs) > 0: self.get_facts_vrfs()
		self.get_facts_static()
		self.get_facts_ospf()
		self.get_facts_bgp(isInstance=False)
		self.get_facts_bgp(isInstance=True)		
		self.get_facts_lldp()
		self.get_facts_int_status()
		# self.vrf_for_vlans()
		self.get_facts_banner()
		self.get_facts_snmp_location()


	""" LLDP PROCESS """

	def get_facts_lldp(self):
		for interface in self.lldp_table:
			phy_if, nbr_attributes = self.physical_interface_lldp_add_ons(interface)
			ifs_on_dict = self.iftype_ifvar["PHYSICAL"]
			if not ifs_on_dict.get(phy_if): ifs_on_dict[phy_if] = {}
			physical_if = ifs_on_dict[phy_if]
			if nbr_attributes: 
				physical_if['neighbour'].update(nbr_attributes)

	"""on lldp-neighbours"""
	def physical_interface_lldp_add_ons(self, interface_shortname):
		"""-->neighbour details 'add_on' for given interface"""
		for phy_if, if_attributes in self.ifphysicals.items():
			if if_attributes["shortname"] == interface_shortname:
				nbr_hn = self.neighbor_hostname(interface_shortname)
				add_on = {}
				add_on['hostname'] = nbr_hn
				add_on['interface'] = self.neighbor_interface(interface_shortname)
				return (phy_if, add_on)
		return (interface_shortname, {})


	def neighbor_hostname(self, interface_shortname):
		return self.lldp_table[interface_shortname]['Device ID']
		
	def neighbor_interface(self, interface_shortname):
		return self.lldp_table[interface_shortname]['Port ID']

	""" SHOW INTERFACE DESCRIPTION PROCESS """

	def get_facts_int_status(self):
		for interface in self.interfaces_table:
			add_ons = self.physical_interface_int_status_add_ons(interface)
			if add_ons:
				physical_if, int_attributes = add_ons[0], add_ons[1]
				physical_if.update(int_attributes)

	def interface_status_para(self, interface_shortname):
		return self.interfaces_table[interface_shortname]

	def physical_interface_int_status_add_ons(self, interface_shortname):
		for int_type in self.if_types:
			for phy_if, if_attributes in self.iftype_ifvar[int_type].items():
				if if_attributes.get("shortname") and if_attributes["shortname"] == interface_shortname:
					# return (self.facts["interfaces"][int_type][phy_if], 
					# 		self.interface_status_para(interface_shortname))
					return (self.iftype_ifvar[int_type][phy_if], 
							self.interface_status_para(interface_shortname))

	""" Interfaces """

	def int_description(self, int_section_config):
		description = ''
		for line in int_section_config:
			if not STR.found(line, " description "): continue
			spl = line.split()
			desc_idx = spl.index('description')+1
			description = " ".join(spl[desc_idx:])
		return description

	""" vlans """
	def vrf_for_vlans(self):
		"""vlan facts attributes using VlanCalculator"""
		for vlan, vlanattr in self.ifvlans.items():			
			vlanattr["vrf"] = self.vrf_for_vlan(vlan)

	def vrf_for_vlan(self, vlan):
		""" -->vrf name for given vlan,	/Child
			default is '' """
		if self.facts['interfaces']['VLAN'].get('Vlan'+str(vlan)):
			return self.facts['interfaces']['VLAN']['Vlan'+str(vlan)]['[vrf]']
		else:
			return ''

	def get_facts_vlans(self, make):
		"""vlan Facts"""
		for vlan, vlanattr in self.ifvlans.items():
			vlanattr['allowedints'] = self.vlan_interfaces(vlan)
			vlID = vlan
			if make == 'juniper': vlID = vlanattr['vl_identifier']
			section_conf = self.get_section_config('vlans', vlID)
			desc = self.vlan_name(section_conf)	
			vlanattr['vlandesc'] = desc

	""" IP Address + n """

	def get_vlans_from_range(self, vl_string):
		if isinstance(vl_string, (list, tuple)):
			for vl in vl_string:
				yield self.sub_get_vlans_from_range(vl)
		elif isinstance(vl_string, str):
			vls = self.sub_get_vlans_from_range(vl_string)
			yield vls

	@staticmethod
	def sub_get_vlans_from_range(vl_string):
		if "-" in vl_string:
			vls = vl_string.split("-")
			for x in range(int(vls[0].strip()),  1+int(vls[1].strip())):
				yield str(x)
		else: 
			yield vl_string.strip()


	def vlan_interfaces(self, vlan):
		"""interfaces list on which given vlan is allowed"""
		allowed_ints = []
		for intType, intType_values in self.iftype_ifvar.items():
			if intType == 'VLAN': continue
			for _int, int_attributes in intType_values.items():
				try:
					if vlan in int_attributes['switchport']['trunk_vlans']:
						allowed_ints.append(_int)
				except:
					pass
		# if len(allowed_ints) == 1: allowed_ints = allowed_ints[0]		
		return allowed_ints

	def shrink_characters(self, ifType, _if):
		"""--> shrinked interface name"""
		shrink_chars = 2
		for int_type, int_types in self.ifs_identifiers.items():
			if ifType == int_type:
				shrink_chars = int_types[STR.if_prefix(_if)]
				break
		return shrink_chars

	""" BANNER """

	def get_facts_banner(self):
		self.facts["[banner]"] = self.banner
	def get_facts_snmp_location(self):
		self.facts["snmp_location"] = self.snmp_location

	######## COMMONS ######

	def matching_static_route(self, facts_statics, route):
		i = 0
		original_route = route
		while True:
			if facts_statics.get(route):
				i += 1
				route = original_route + "_" + str(i)
			else:
				break
		return i

	def add_aaza(self, item, items, item_template):
		if item not in items:
			items[item] = item_template()


# ---------------------------------------------------------------------------- #
