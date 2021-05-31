__doc__ = "Excel Facts Generation from configuration output"

"""
Mandatory Requirements 
======================
pandas and it’s dependent packages (xlrd, openpyxl)
nettoolkit

Usage Example
=============
from facts_generator import FactsGen

# # single file with all outputs
datapath = "c:/Users/ALI/OneDrive/Desktop/Data/"
capture_file = datapath + "switch_op.log"

# # output distributed in mutliple files
# conf = datapath + 'conf.log' 
# intf = datapath + "interfaces.log"
# lldp = datapath + "lldp.log"
# capture_file = {'config': conf, 'interfaces': intf, 'neighbour': lldp }

##### Executions #####
fg = FactsGen()						# 1. create object
fg.parse(capture_file)				# 2. parse captures
# ------------------------------------------------ #
#             OPTIONAL / CUSTOM VARS
#               section insert here
# custom processes on fg.facts to add/modify facts
# ------------------------------------------------ #
fg.process(						# 3. Process output
    # map_sheet=custom_map_excelsheet,                  # optional
    # customer_var=additional_customer_variables_dict,  # optional
	)
fg.to_file(datapath)			# 4. write output facts to given path, "." for local path



# --------------------------------------------------------------------


# - For Juniper capture below outputs -
# sh_run = "sh_config.log"
# sh_lldp = "sh_lldp_nei.log"
# sh_int = "sh_int_desc.log"


"""

__ver__ = "0.0.5"

__all__ = [ "FactsGen" ]

from .exec_ro import FactsGen