

from facts_generator import FactsGen

# # single file with all outputs
datapath = "c:/Users/ALI/OneDrive/Desktop/Data/"
capture_file = datapath + "switch_op.log"

# # output distributed in mutliple files
# conf = datapath + 'conf.log' 
# intf = datapath + "interfaces.log"
# lldp = datapath + "lldp.log"
# capture_file = {'config': conf, 'interfaces': intf, 'neighbour': lldp }

fg = FactsGen()
fg.parse(capture_file)

# custom processes on fg.facts to add/modify facts

fg.process(
    # map_sheet=custom_map_excelsheet,                  # optional
    # customer_var=additional_customer_variables_dict,  # optional
)
fg.to_file(datapath)
