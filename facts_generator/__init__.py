__doc__ = "Excel Facts Generation from configuration output"

"""
Mandatory Requirements 
======================
pandas and it’s dependent packages (xlrd, ...)
nettoolkit

Usage Example
=============
from facts_generator import FactsGen

##### define capture files in a dictionary with defined keys #####
sh_run = "show_run.log"
sh_int = "show_int_status.log"
sh_lldp = "show_lldp_neighbor.log"

captures = {
	'config': sh_run,
	'interfaces': sh_int,
	'neighbour': sh_lldp,
	}

##### Executions #####
fg = FactsGen()					# 1. create object
fg.parse(captures)				# 2. parse captures
# ------------------------------------------------ #
#             OPTIONAL / CUSTOM VARS
#               section insert here
# ------------------------------------------------ #
fg.process(						# 3. Process output
	# map_sheet=map_sheet,			# optional - std to custom variable map sheet
	# customer_var=sv.custom_vars,	# optional - customer variables
	)
output_path = "."
fg.to_file(output_path)			# 4. write output facts to given path


# ------------------------------------------------ #
#             OPTIONAL / CUSTOM VARS
# ------------------------------------------------ #
# ##### Define custom changes #####
# map_sheet = "CUSTOMER/std_custom_var_maps.xlsx"

# ##### Executions / define customer variables #####
# import CUSTOMER
# custom_variables = "CUSTOMER/customer_variables.xlsx"
# sv = CUSTOMER.StaticVar(fg.facts)
# sv.create(custom_variables)
# st = CUSTOMER.StaticTables(fg.facts)
# st.create()

# # [Note: sv.custom_vars => customer_var]
# ------------------------------------------------ #

# --------------------------------------------------------------------


# - For Juniper capture below outputs -
# sh_run = "sh_config.log"
# sh_lldp = "sh_lldp_nei.log"
# sh_int = "sh_int_desc.log"


"""

__ver__ = "0.0.3"

__all__ = [ "FactsGen" ]

from .exec_ro import FactsGen