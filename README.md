use Execute_Read_Only_Mode function to read the output and generate facts
	mandatory command output requires : 
	# Cisco 
	'sh run'
	'sh lldp nei'
	'sh int status'

	# Juniper 
	'show configuration | no-more'
	'show lldp neighbors | no-more'
	'show interfaces descriptions | no-more'
	