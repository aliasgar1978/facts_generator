


class ParametersTemplate():

	@staticmethod
	def ifvlan():
		return {
			'vlandesc': '',				# vlan description
			'description': '',			# interface vlan description
			'vrf': 'global',
			'shortname': '',
			'dhcphelpers': [],
			'dhcpv6helpers': [],
			'inet4': {'address': '' },
			'inet6': {'address': '', 'linklocal': ''},
		}

	@staticmethod
	def ifphysical():
		return {
			'description': '',
			'vrf': 'global',
			'shortname': '',
			'linktype': '',
			'l2orl3': '',
			'switchport': {
				'mode': '',
				'accessvlan': '',
				'voicevlan': '',
				'nativevlan': '',
				'trunkvlans': [],
				'encapsulation': '',
				'negotiate': '',	
			},
			'neighbour': {'interface': '', 'hostname': ''},
			'inet4': {'address': '' },
			'inet6': {'address': '', 'linklocal': ''},
			'pomode': '',
			'ponumber': '',
		}

	@staticmethod
	def ifloopback():
		return {
			'description': '',
			'vrf': 'global',
			'shortname': '',
			'inet4': {'address': '' },
			'inet6': {'address': '', 'linklocal': ''},
		}

	@staticmethod
	def ifaggregate():
		return {
			'description': '',
			'shortname': '',
			'inet4': {'address': '' },
			'inet6': {'address': '', 'linklocal': ''},
			'vlanmembers': [],
			'intmembers': [],
		}

	@staticmethod
	def iftunnel():
		return {
			'description': '',
			'vrf': 'global',
			'shortname': '',
			'l2orl3': '',
			'switchport': {
				'mode': '',
				'accessvlan': '',
				'voicevlan': '',
				'nativevlan': '',
				'trunkvlans': [],
				'encapsulation': '',
				'negotiate': '',	
			},
			'inet4': {'address': '' },
			'inet6': {'address': '', 'linklocal': ''},
			'source': '',
			'destination': '',			
		}

	@staticmethod
	def ifrange():
		return {
			'description': '',
			'vrf': 'global',
			'shortname': '',
			'inet4': {'address': '' },
			'inet6': {'address': '', 'linklocal': ''},
			'members': [],
			'switchport': {
				'mode': '',
				'accessvlan': '',
				'voicevlan': '',
				'nativevlan': '',
				'trunkvlans': [],
				'encapsulation': '',
				'negotiate': '',	
			},
		}

	@staticmethod
	def ifmanagement():
		return {
			'description': '',
			'vrf': 'global',
			'shortname': '',
			'inet4': {'address': '' },
			'inet6': {'address': '', 'linklocal': ''},
		}

	@staticmethod
	def var():
		return {
			'hostname': '',
			'make':'', 'model': '', 'template': '', 
			'ntpservers': [],
			'nameservers': [],
			'snmpservers': [],
			'syslogservers': [],
			'authservers': [],
		}

def iftype_templ(item):
	itt = {
		"LOOPBACK": ParametersTemplate.ifloopback, 
		"AGGREGATED": ParametersTemplate.ifaggregate, 
		"PHYSICAL": ParametersTemplate.ifphysical, 
		"TUNNEL": ParametersTemplate.iftunnel,
		"VLAN": ParametersTemplate.ifvlan,
		"RANGE": ParametersTemplate.ifrange,
		"MANAGEMENT": ParametersTemplate.ifmanagement,
	}
	return itt[item]