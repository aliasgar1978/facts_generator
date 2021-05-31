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
	
=============================================
#         - USAGE GUIDELINES - 				#
=============================================
from facts_generator import FactsGen

# OPTION 1 # single file with all outputs
datapath = "c:/Users/xxxx/Desktop/Data/"		# path
capture_file = datapath + "switch_op.log"

# OPTION 2 # output distributed in mutliple files
# conf = datapath + 'conf.log' 
# intf = datapath + "interfaces.log"
# lldp = datapath + "lldp.log"
# capture_file = {'config': conf, 'interfaces': intf, 'neighbour': lldp }

fg = FactsGen()
fg.parse(capture_file)

# custom processes on fg.facts to add/modify facts  ## OPTIONAL ##

fg.process(
    # map_sheet=custom_map_excelsheet,                  # optional
    # customer_var=additional_customer_variables_dict,  # optional
)
fg.to_file(datapath)
