# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from collections import OrderedDict
import pandas as pd 

from .init_tasks import InitTask
from .tasks import Tasks, flat_dict, merge_vlan_intVlan

# ---------------------------------------------------------------------------- #

table_items = ('interfaces', 'vlans', 'statics', 'vrfs', 'ospf')

# ---------------------------------------------------------------------------- #
# General Usage functions
# ---------------------------------------------------------------------------- #

def create_add_map_def(n):
	""" Create an Address MAP Dictionary for n number of IPs """
	dic = {}
	for i in range(n):
		dic['address_+' + str(i) + "]"] = "[Subnet+" + str(i)+ "]"
		dic['address_+' + str(i) + "/mm]"] = "[Subnet+" + str(i)+ "/mm]"
	return dic

# ---------------------------------------------------------------------------- #
# Class: Convert Device Facts to DataFrames
# ---------------------------------------------------------------------------- #

# DEVICE SPECIFIC VAR ATTRIBUTES
def device_var_attrib(dev_var_attribs, varattrib=None):
    '''--> append device var attribute dict'''
    if varattrib is None: varattrib = {"FIND":[], "REPLACE":[]}
    for k, v in dev_var_attribs.items():
        varattrib['FIND'].append(k)
        varattrib['REPLACE'].append(v)
    return varattrib

class FactsToDf():

	def __init__(self, 
		facts, 
		customer_var=None,
		):
		self.customer_var = customer_var
		self.process_table(facts)
		self.process_var(facts)

	def set_custom_variables(self, map_sheet=None):
		if not map_sheet: return None
		self.custom_table_header_update(map_sheet)
		self.custom_var_update(map_sheet)

	@staticmethod
	def get_custom_variables_dict(map_sheet, sheet_name):
		df_map = pd.read_excel(map_sheet, sheet_name=sheet_name).fillna("")
		df_map = df_map.set_index("STANDARD")
		df_map = df_map[df_map['CUSTOM'] != ""]
		return df_map.to_dict()["CUSTOM"]

	def process_var(self, facts):
		self.var_facts = {k: v for k, v in facts.items() 
						if k  not in table_items }
		var_facts = device_var_attrib(self.var_facts)
		varattrib = self.dataFrame_var(var_facts)
		self.df_var = pd.DataFrame(varattrib)
		if self.customer_var:
			self.custom_var_append()

	def custom_var_update(self, map_sheet):
		self.df_var = self.df_var.set_index("FIND")
		self.df_var = self.df_var.T
		custom_vars = self.get_custom_variables_dict(map_sheet, 'var')
		self.df_var.rename(columns=custom_vars, inplace=True)
		self.df_var = self.df_var.T

	def custom_var_append(self):
		self.df_customer_var = pd.DataFrame(self.customer_var)
		self.df_var = self.df_var.append(self.df_customer_var)

	def process_table(self, facts):
		merge_vlan_intVlan(facts)
		table_facts = {k: v for k, v in facts.items() 
					if k in table_items }
		self.df_table = self.dataFrame_table(table_facts)
		self.df_table.rename(
			columns=create_add_map_def(Tasks.number_of_max_extended_ips), 
			inplace=True)


	def custom_table_header_update(self, map_sheet):
		custom_tables = self.get_custom_variables_dict(map_sheet, 'tables')
		self.df_table.rename(columns=custom_tables, inplace=True)

	def dataFrame_table(self, table_facts):
		table = {}

		# -- interfaces
		if table_facts.get('interfaces'):
			for int_type, all_ints_dict in table_facts['interfaces'].items():
				for int_name, int_dict in all_ints_dict.items():
					table[int_name] = flat_dict(int_dict, int_type)
					table[int_name].update({'[Contender]': int_name})

		# -- static routes
		if table_facts.get('statics'):
			for route_x, route_dict in table_facts['statics'].items():
				table[route_x] = flat_dict(route_dict, 'static_route')

		# -- vrfs
		if table_facts.get('vrfs'):
			for vrf_x, vrf_dict in table_facts['vrfs'].items():
				table[vrf_x] = flat_dict(vrf_dict, 'VRFS')

		# -- ospf
		if table_facts.get('ospf'):
			for _x, _dict in table_facts['ospf'].items():
				table[_x] = flat_dict(_dict, 'OSPF')

		df_table = pd.DataFrame.from_dict(table).T
		return df_table

	def dataFrame_var(self, var_facts):
		target_d = { 'FIND':[], 'REPLACE':[] }
		for x, y in zip(var_facts['FIND'], var_facts['REPLACE']):
			if not isinstance(y, dict):
				target_d['FIND'].append(x)
				target_d['REPLACE'].append(y)
				continue
			td = flatten_dict(x, y)
			for k, v in td.items():
				target_d['FIND'].append(k)
				target_d['REPLACE'].append(v)
		return target_d


def flatten_dict(parent_key, child_dict):
	new_dict = {}
	for key, value in child_dict.items():
		if not isinstance(value, (dict,OrderedDict)):
			new_dict[parent_key+"_"+key] = value
		else:
			new_dict.update(flatten_dict(parent_key+"_"+str(key), value))
	return new_dict


# ---------------------------------------------------------------------------- #
# Class : Processing output
# ---------------------------------------------------------------------------- #

class Output_Process():

	@property
	def var_facts(self):
		return self.fToD.var_facts

	@property
	def facts(self):
		return self._facts

	@property
	def dataframe_args(self):
		return self.df_args

	def convert_and_add_custom_vars_to_dataframes(self, map_sheet, customer_var):
		self.fToD = FactsToDf(self.facts,
			customer_var=customer_var,
			)
		self.fToD.set_custom_variables(map_sheet)
		hostname = self.facts['[dev_hostname]']
		tables_df = self.fToD.df_table
		var_df = self.fToD.df_var
		index = True
		self.df_args = {'hostname':hostname, 
			'tables': tables_df, 
			'var': var_df, 
			'index': index
			}

	def output_parse(self, files=None):
		if not isinstance(files, (dict, str)):
			raise Exception("Incorrect Input `files` should be in dict of lists or single file string")
		iT = InitTask(files=files)
		self._facts = iT.tasks.facts
		self.F = iT.tasks



# ---------------------------------------------------------------------------- #
