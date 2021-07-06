# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from collections import OrderedDict
import pandas as pd 

from .init_tasks import InitTask
from .tasks import Tasks
from nettoolkit import ConvDict

# ---------------------------------------------------------------------------- #
# Class: Convert Device Facts to DataFrames
# ---------------------------------------------------------------------------- #


class FactsToDf():

	def __init__(self, 
		facts, 
		customer_var=None,
		):
		self.customer_var = customer_var
		self.var_dict(facts)
		self.table_dict(facts)
		self.convert_dictionary()

	def convert_dictionary(self):
		facts = {'table': self.table_dic}
		facts.update(self.var_dic)
		cd = ConvDict(facts)
		cd.set_var_table_keys(var='var', table='table')
		cd.set_index_keys_parents()
		self.var_df = cd.to_dataframe('var')
		self.table_df = cd.to_dataframe('table')				

	def table_dict(self, facts):
		self.table_dic = {k:v for k,v in facts.items() if k != 'var'} 
		del(self.table_dic['instances'])
	def var_dict(self, facts):
		self.var_dic = {k:v for k,v in facts.items() if k == 'var'} 


# ---------------------------------------------------------------------------- #
# Class : Processing output
# ---------------------------------------------------------------------------- #

class Output_Process():

	# @property
	# def var_facts(self):
	# 	return self.fToD.var_facts

	@property
	def facts(self):
		return self._facts

	@property
	def dataframe_args(self):
		return self.df_args

	def convert_and_add_custom_vars_to_dataframes(self, map_sheet, customer_var):
		self.fToD = FactsToDf(self.facts)
		self.var_df = self.fToD.var_df
		self.table_df = self.fToD.table_df
		hostname = self.facts['var']['hostname']
		self.df_args = {'hostname': hostname,'var': self.var_df, 'table': self.table_df }

	def output_parse(self, files=None):
		if not isinstance(files, (dict, str)):
			raise Exception("Incorrect Input `files` should be in dict of lists or single file string")
		iT = InitTask(files=files)
		self._facts = iT.tasks.jfacts
		self.F = iT.tasks



# ---------------------------------------------------------------------------- #
