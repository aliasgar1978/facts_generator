# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from collections import OrderedDict
from nettoolkit import IPv4, IPv6, addressing, IP, STR, LST

from .tasks import Tasks

# ---------------------------------------------------------------------------- #
# Cisco CONSTANTS
# ---------------------------------------------------------------------------- #

CISCO_IFS_IDENTIFIERS = {
	"VLAN": {'Vlan':2,},
	"TUNNEL": {'Tunnel':2,},
	"LOOPBACK": {'Loopback':2,} ,
	"AGGREGATED": {'Port-channel':2,},
	"PHYSICAL": {'Ethernet': 2, 
		'FastEthernet': 2,
		'GigabitEthernet': 2, 
		'TenGigabitEthernet': 2, 
		'FortyGigabitEthernet':2, 
		'TwentyFiveGigE':3, 
		'TwoGigabitEthernet': 2,
		'HundredGigE':2,
		'AppGigabitEthernet': 2,
		},
}
CISCO_STARTERS = {
	'ifs': 'interface',
	'vrfs': 'vrf definition',
	'vlans': 'vlan',
	'ospf': 'router ospf',
	'bgp': 'router bgp',
	'bgp_af': ' address-family',
	'route': 'ip route',
}
CISCO_LLDP_COL_HEADER_INDEXES = {
	"Device ID":    ( 0, 20), 
	"Local Intf":   (20, 35), 
	"Hold-time":    (35, 46), 
	"Capability  ": (46, 62), 
	"Port ID":      (62, 90),
	}

# ---------------------------------------------------------------------------- #
# Cisco TASKS
# ---------------------------------------------------------------------------- #
class CiscoTasks(Tasks):
	"""Cisco Tasks"""

	ifs_identifiers = CISCO_IFS_IDENTIFIERS
	starter = CISCO_STARTERS
	lldp_col_header_indexes = CISCO_LLDP_COL_HEADER_INDEXES

	def get_section_config(self, section, name, af_only=False):
		"""--> Section config in list format"""
		section_config = []
		start = False
		for line in self.run_list:
			if line.startswith(self.starter[section] + " " + str(name) + "\n"):
				start = True
			if start:
				section_config.append(line.rstrip())
				if af_only and line.rstrip() == ' !': break
				elif line.rstrip() == "!": break
		return section_config

	""" AAZA """

	def aaza(self):
		"""Aaza of device"""
		for line in self.run_list:
			# Interfaces configs
			if line.startswith(self.starter['ifs']):
				self.ifs.append(line.split()[-1])
				for int_type, int_types in self.ifs_identifiers.items():
					for int_type_type in int_types:
						if int_type_type in self.ifs[-1]:
							self.if_types[int_type].append(self.ifs[-1])
							break
				continue
			# vrf definitions
			if line.startswith(self.starter['vrfs']):
				self.vrfs.append(line.split()[-1])
				continue
			# vlans
			if (line.startswith(self.starter['vlans'])
				and not line.startswith("vlan internal")
				):
				try:
					self.vlans.append(int(line.split()[-1]) )
				except:
					pass
				continue
			# ospf section
			if line.startswith(self.starter['ospf']):
				self.ospf.append(" ".join(line.split()[2:]))
				continue
			# bgp section
			if line.startswith(self.starter['bgp']):
				self.bgp.append(line.split()[-1])
				continue
			# static routes section
			if line.startswith(self.starter['route']):
				self.routes.append(line)
				continue
			# snmp string
			if line.startswith("snmp-server location "):
				self.snmp_location = line[21:].strip()
			# exec banner
			if line.startswith("banner exec "):
				self.banner = line[14:].strip()

		# bgp section config for vrf
		self.facts["bgp"] = {}
		if self.bgp:
			self.bgp_aaza(self.get_section_config('bgp', self.bgp[0]))


		return {'if_types': self.if_types, 
				'ifs': self.ifs, 
				'vrfs': self.vrfs, 
				'vlans': self.vlans,
				'ospf': self.ospf,
				'bgp': self.bgp,
				'bgp_af': self.bgp_af,
				'route': self.routes,
				}

	def interface_aaza(self):
		"""Interface Aaza from interface status"""
		headers = None
		self.interfaces_table = {}
		for line in self.int_status_list:
			if STR.is_blank_line(line): continue
			if headers is None:
				headers = STR.header_indexes(line)
				headers['Speed'][0] -= 1
				headers['Duplex'][1] -= 1
				del(headers["Name"])
				del(headers["Vlan"])
				continue
			else:
				for header_item, idxes in headers.items():
					detail = line[idxes[0]:idxes[1]].strip()
					if header_item == 'Port':
						if not self.interfaces_table.get(detail):
							self.interfaces_table[detail] = {}
							port_detail = self.interfaces_table[detail]
							continue
					port_detail[header_item] = detail
				port_detail['l2_status'] = port_detail['Status']
				del(port_detail['Status'])

	def bgp_aaza(self, bgp_list):
		"""bgp adddress family lists"""
		for line in bgp_list:
			if line.startswith(self.starter['bgp_af']):
				self.bgp_af.append(" ".join(line.split()[1:]))
				continue

	def lldp_aaza(self):
		"""lldp aaza from lldp neighbors"""
		header_found = False
		self.lldp_table = {}
		for line in self.lldp_list:
			if STR.is_blank_line(line): continue
			if STR.found(line, "Total entries"): break
			if not header_found:
				list_of_truths = [item in line for item in self.lldp_col_header_indexes]
				header_found = False not in list_of_truths
				continue
			if header_found:
				for header_item, idxes in self.lldp_col_header_indexes.items():
					if header_item == 'Local Intf':
						short_interface = line[idxes[0]:idxes[1]].strip()
						if not self.lldp_table.get(short_interface):
							self.lldp_table[short_interface] = {}
							int_lldp_device = self.lldp_table[short_interface] 
							break
					else:
						continue
				for header_item, idxes in self.lldp_col_header_indexes.items():
					if header_item != 'Local Intf':
						int_lldp_device[header_item] = line[idxes[0]:idxes[1]].strip()

	""" Facts """

	def get_facts_hostname(self):
		"""device hostname"""
		for line in self.run_list:
			if line.startswith("hostname "):
				self.facts['[dev_hostname]'] = line.split()[1]
				break

	def get_facts_interfaces(self):
		"""Interface Facts"""
		self.facts["interfaces"] = {}
		facts_ifs = self.facts["interfaces"]
		for ifType, _ifs in self.if_types.items():
			facts_ifs[ifType] = OrderedDict()
			facts_if = facts_ifs[ifType]
			for _if in _ifs:
				facts_if[_if] = {}
				ifFacts = facts_if[_if]
				shrink_chars = self.shrink_characters(ifType, _if)
				ifFacts['short_name'] = STR.shrink_if(_if, shrink_chars)
				if ifType in ('AGGREGATED', 'LOOPBACK', 'VLAN', 'TUNNEL'): 
					ifFacts['int_number'] = int(ifFacts['short_name'][2:])
				section_conf = self.get_section_config('ifs', _if)
				ifFacts['address'] = self.int_address(section_conf)
				ifFacts['description'] = self.int_description(section_conf)
				ifFacts['port_status'] = self.int_port_status(section_conf)
				ifFacts['udld_state'] = self.int_udld_state(section_conf)
				ifFacts['channel_group'] = self.int_ether_channel(section_conf)
				ifFacts['switchport'] = self.int_vlans(section_conf)
				ifFacts['[vrf]'] = self.int_vrf(section_conf)
				ifFacts['helpers'] = self.int_helpers(section_conf)

	def get_facts_vrfs(self):
		"""vrf Facts"""
		self.facts["vrfs"] = OrderedDict()
		facts_vrfs = self.facts["vrfs"]
		for vrf in self.vrfs:
			section_conf = self.get_section_config('vrfs', vrf)
			facts_vrfs[vrf] = self.vrf_rd_rt(section_conf) 
			facts_vrfs[vrf].update({'[vrf]': vrf})

	def get_facts_vlans(self):
		"""vlan Facts"""
		self.facts["vlans"] = OrderedDict()
		facts_vlans = self.facts["vlans"]
		for vlan in self.vlans:
			facts_vlans[vlan] = {}
			section_conf = self.get_section_config('vlans', vlan)
			desc = self.vlan_name(section_conf)	
			facts_vlans[vlan]['vl_description'] = desc
			facts_vlans[vlan]['allowed_ints'] = self.vlan_interfaces(vlan)

	def get_facts_static(self):
		"""static route facts"""
		self.facts["statics"] = OrderedDict()
		facts_statics = self.facts["statics"]
		for route in self.routes:
			route, route_attributes = self.static_route(route)
			msr = self.matching_static_route(facts_statics, route)
			if msr: route = route + "_" + str(msr)
			facts_statics[route] = route_attributes


	def get_facts_ospf(self):
		"""ospf facts"""
		self.facts["ospf"] = {}
		facts_ospfs = self.facts["ospf"]
		for instance in self.ospf:
			facts_ospfs[instance] = {}
			section_conf = self.get_section_config('ospf', instance)
			facts_ospfs[instance]['router_id'] = self.ospf_router_id(section_conf)
			facts_ospfs[instance]['area_summaries'] = self.ospf_area_summary(section_conf)
			facts_ospfs[instance]['area_networks'] = self.ospf_area_network(section_conf)		

	def get_facts_bgp(self, isInstance=False):
		"""bgp facts"""
		facts_bgps = self.facts["bgp"]
		for instance in self.bgp_af if isInstance else self.bgp:
			inst = instance if isInstance else 'global'
			facts_bgps[inst] = {}
			gl = facts_bgps[inst]
			what = 'bgp_af' if isInstance else 'bgp'
			section_conf = self.get_section_config(what, instance, af_only=True)
			gl['router_id'] = self.bgp_router_id(section_conf)
			if what == 'bgp': gl['AS'] = instance
			peer_groups = self.bgp_peer_groups(section_conf)
			for peer in peer_groups:
				gl['peer_group'] = {}
				pg = gl['peer_group']
				if not pg.get(peer): pg[peer] = {}
				pg_peers = pg[peer]
				pg_peers['peers'] = self.bgp_peer_group_neighbors(section_conf, peer)
				pg_peers['remote_as'] = self.bgp_peer_group_remote_as(section_conf, peer)

	""" VLAN """
	def vlan_name(self, int_section_config):
		"""set vlan name for each vlans"""
		name = ''
		for line in int_section_config:
			if line.lstrip().startswith("name"):
				name = line[6:]
				break
		return name

	""" VRF """

	def vrf_rd_rt(self, int_section_config):
		"""vrf rd/rt aaza"""
		router_id, rd, rt_import, rt_export = '', '', '', ''
		for line in int_section_config:
			if line.lstrip().startswith("rd "):
				rd = line.split()[-1]
				router_id = rd.split(":")[0]
				continue
			if line.lstrip().startswith("route-target export"):
				rt_export = line.split()[-1]
				continue
			if line.lstrip().startswith("route-target import"):
				rt_import = line.split()[-1]
				continue
		return {'router_id': router_id,
				'rd': rd, 
				'rt_export': rt_export, 
				'rt_import':rt_import}

	""" Interfaces """

	def int_port_status(self, int_section_config):
		"""status of port"""
		status = 'up'
		for line in int_section_config:
			if line.lstrip().startswith("shutdown"):
				status = 'administratively down'
				break
		return status

	def int_udld_state(self, int_section_config):
		"""interface udld status"""
		udld = 'disable'
		for line in int_section_config:
			if line.lstrip().startswith("udld port "):
				udld = line.split()[-1]
				break
		return udld

	def int_vrf(self, int_section_config):
		"""--> vrf name for particular interfaces"""
		vrf = ''
		for line in int_section_config:
			if (line.lstrip().startswith("vrf forwarding ")
				or line.lstrip().startswith("ip vrf ")
				):
				vrf = line.split()[-1]
				break
		return vrf

	def int_helpers(self, int_section_config):
		"""--> helper ip's for particular interface"""
		helpers, v6helpers = [], []
		for line in int_section_config:
			if line.lstrip().startswith("ip helper-address "):
				helpers.append(line.split()[-1])
				continue
			if line.lstrip().startswith("ipv6 dhcp relay destination"):
				v6helpers.append(line.split()[-1])
				continue
		return {'v4helpers': helpers, 
				'v6helpers': v6helpers}

	def int_address(self, int_section_config):
		"""IP Addressing on interface"""
		subnet = ''
		v4subnet_mask = ''
		v4subnet_invmask = ''
		v6subnet = ''
		exluded_v6_candidates = ('link-local', 'anycast')
		for line in int_section_config:
			if not subnet and line.lstrip().startswith("ip address "):
				binmask = line.split()[-1]
				ip = line.split()[-2] + "/" + str(IP.bin2dec(binmask))
				subnet = IPv4(ip)
				v4subnet_mask = subnet.binmask
				v4subnet_invmask = subnet.invmask
				continue
			if not v6subnet and line.lstrip().startswith("ipv6 address "):
				l = line.split()
				if l[-1] in exluded_v6_candidates: continue
				v6subnet = IPv6(l[-1])
				break

		address_vars = {'v4subnet': subnet,
						'[v4subnet_mask]': v4subnet_mask,
						'[v4subnet_invmask]': v4subnet_invmask,
						'v6subnet': v6subnet, 
						}
		address_vars.update(self.int_v4address_extend(subnet))
		return address_vars

	def int_vlans(self, int_section_config):
		"""Switching on interface"""
		mode = None
		access_vlan = 1
		voice_vlan = None
		native_vlan = 1
		trunk_vlans = []
		for line in int_section_config:
			if line.lstrip().startswith("switchport mode "):
				mode = line.split()[-1]
				continue
			if line.lstrip().startswith("switchport trunk native vlan "):
				native_vlan = int(line.split()[-1])
				continue
			if line.lstrip().startswith("switchport access vlan "):
				access_vlan = int(line.split()[-1])
				continue
			if line.lstrip().startswith("switchport voice vlan "):
				voice_vlan = int(line.split()[-1])
				continue
			if line.lstrip().startswith("switchport trunk allowed vlan "):
				for v in self.get_vlans_from_range(line.split()[-1].split(",")):
					trunk_vlans.extend(v)
				continue
		trunk_vlans =[int(vl) for vl in trunk_vlans]
		variants = LST.list_variants(trunk_vlans)
		return {'mode': mode,
				'access_vlan': access_vlan,
				'voice_vlan': voice_vlan,
				'native_vlan': native_vlan,
				'trunk_vlans': trunk_vlans,
				'ssv_allowed_vlns': variants['ssv_list'],
				'csv_allowed_vlns': variants['csv_list'], }

	def int_ether_channel(self, int_section_config):
		"""Port Channel config on interface"""
		channel_group = None
		channel_group_mode = None
		for line in int_section_config:
			if line.lstrip().startswith("channel-group "):
				l = line.split()
				channel_group = l[1]
				channel_group_mode = l[-1]
				break
		return {'number': channel_group,
				'mode': channel_group_mode,}

	""" Statics """

	def static_route(self, route):
		"""--> static route parameters """
		if STR.found(route, ' name '):
			route, name = route.split(" name ")
		else: 
			name = ""
		name = name.rstrip()
		spl_route = route.split(" track ")
		track = spl_route[-1] if len(spl_route) == 2 else None
		route = route.split(' tag ')
		tag = route[1].rstrip() if len(route) == 2 else None
		route = route[0].split("ip route ")[-1].split()
		vrf = route[1] if route[0] == 'vrf' else None
		route_idx = 2 if vrf else 0
		_subnet = route[route_idx] + "/" + str(IP.bin2dec(route[route_idx+1]))
		subnet = str(addressing(_subnet))
		subnet_header = vrf + "_" + str(subnet) if vrf else str(subnet)
		try:
			next_hop = addressing(route[route_idx+2] + "/32")
		except:
			next_hop = None
		attribute = {'name': name, 'subnet': subnet }
		if track: attribute.update({'track': track})
		if vrf: attribute.update({'[vrf]': vrf})
		if tag: attribute.update({'tag': tag})
		if next_hop: attribute.update({'next_hop': next_hop})

		return subnet_header, attribute

	""" OSPF """

	def ospf_router_id(self, section_config):
		"""--> OSPF: Router ID"""
		router_id = None
		for line in section_config:
			if line.lstrip().startswith("router-id "):
				router_id = line.split()[-1]
				break
		return router_id

	def ospf_area_summary(self, section_config):
		"""--> OSPF: area summaries"""
		summary = {}
		for line in section_config:
			l = line.lstrip().split()
			if l[0] == 'area' and l[2] == 'range':
				area = l[1]
				_subnet = l[-2] + "/" + str(IP.bin2dec(l[-1]))
				subnet = IPv4(_subnet)
				if not summary.get(area):
					summary[area] = []
				summary[area].append(subnet)
		return summary

	def ospf_area_network(self, section_config):
		"""--> OSPF: Networks per area"""
		network_areas = {}
		for line in section_config:
			if line.lstrip().startswith("network "):
				l = line.lstrip().split()
				area = l[-1]
				_subnet = l[1] + "/" + str(IP.inv2dec(l[2]))
				subnet = IPv4(_subnet)
				if not network_areas.get(area):
					network_areas[area] = []
				network_areas[area].append(subnet)
		return network_areas

	""" BGP """

	def bgp_router_id(self, section_config):
		"""--> BGP: Router ID"""
		router_id = None
		for line in section_config:
			if line.lstrip().startswith("bgp router-id "):
				router_id = line.split()[-1]
				break
		return router_id

	def bgp_peer_groups(self, section_config):
		"""--> BGP: peer group names"""
		peer_groups = []
		for line in section_config:
			l = line.lstrip().split()
			if l[-1] == 'peer-group':
				peer_groups.append(l[-2])
		return peer_groups

	def bgp_peer_group_remote_as(self, section_config, peer_group_name):
		"""--> BGP: Remote as number for given peer"""
		for line in section_config:
			l = line.lstrip().split()
			if l[1] == peer_group_name and l[2] == 'remote-as':
				return l[-1]

	def bgp_peer_group_neighbors(self, section_config, peer_group_name):
		"""--> BGP: Neighbour details for given peer"""
		peer_group_neighbours = {}
		last_peer = ''
		for line in section_config:
			l = line.lstrip().split()
			if l[-1] == peer_group_name:
				peer_group_neighbours[l[1]] = {}
				last_peer = l[1]
				continue
			if last_peer and line.lstrip().startswith('neighbor ' + last_peer ):
				peer_group_neighbours[last_peer]['description'] = " ".join(l[3:])
		return peer_group_neighbours


# ---------------------------------------------------------------------------- #
