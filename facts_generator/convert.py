# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from collections import OrderedDict
import pandas as pd 

from .init_tasks import InitTask
from .tasks import Tasks, flat_dict

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

	def __init__(self, facts):
		self.process_table(facts)
		self.process_var(facts)

	def process_var(self, facts):
		self.var_facts = {k: v for k, v in facts.items() 
						if k  not in ('interfaces', 'vlans', 'bgp') }
		var_facts = device_var_attrib(self.var_facts)
		varattrib = self.dataFrame_var(var_facts)
		self.df_var = pd.DataFrame(varattrib)

	def process_table(self, facts):
		table_facts = {k: v for k, v in facts.items() 
					if k == 'interfaces' }
		self.df_table = self.dataFrame_table(table_facts)
		self.df_table.rename(
			columns=create_add_map_def(Tasks.number_of_max_extended_ips), 
			inplace=True)

	def dataFrame_table(self, table_facts):
		table = {}
		for int_type, all_ints_dict in table_facts['interfaces'].items():
			for int_name, int_dict in all_ints_dict.items():
				table[int_name] = flat_dict(int_dict, int_type)
				table[int_name].update({'[Contender]': int_name})
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
	def __init__(self, files=None):
		self.output_parse(files)

	@property
	def var_facts(self):
		return self.fToD.var_facts

	@property
	def facts(self):
		return self._facts

	@property
	def dataframe_args(self):
		return self.df_args

	def get_dataframes_args(self, iT):
		self.fToD = FactsToDf(iT.tasks.facts)
		tables_df = self.fToD.df_table
		hostname = iT.tasks.facts['[dev_hostname]']
		var_df = self.fToD.df_var
		index = True
		return {'hostname':hostname, 'tables': tables_df, 'var': var_df, 'index': index}

	def output_parse(self, files=None):
		if not isinstance(files, dict):
			raise Exception("Incorrect Input `files` should be in dict of lists")
		iT = InitTask(files=files)
		self._facts = iT.tasks.facts
		self.df_args = self.get_dataframes_args(iT)


# ---------------------------------------------------------------------------- #
