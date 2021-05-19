
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
from nettoolkit import STR, IO, Default, XL_WRITE, Multi_Execution

from .convert import Output_Process

# -----------------------------------------------------------------------------

class FactsGen():

	def __str__(self): return self._repr()
	
	@property
	def facts(self): return self.op.facts
	@property
	def df_dic(self): return self.pod
	@property
	def xl_file(self): return self.xl_op_file
	@property
	def dataframes_dict(self): return self.op.dataframe_args

	def parse(self, captures):
		self.op = Output_Process()
		self.op.output_parse(captures)

	def process(self, map_sheet=None, customer_var=None):
		self.op.convert_and_add_custom_vars_to_dataframes(map_sheet, customer_var)

	def to_file(self, output_path):
		self.xl_op_file = XL_WRITE(folder=output_path, **self.dataframes_dict)
