
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
from nettoolkit import STR, IO, Default, XL_WRITE, Multi_Execution

from .convert import Output_Process

# -----------------------------------------------------------------------------

class Execute_Read_Only_Mode(Multi_Execution):

	def __str__(self): return self._repr()

	def __init__(self, captures, output_path):
		self.captures = captures
		self.output_path = output_path
		super().__init__(self.captures)
		self.start()
		self.end()

	@property
	def df_dic(self): return self.pod
	@property
	def xl_file(self): return self.xl_op_file

	def execute(self, hn):
		processed_op = Output_Process(files=self.captures[hn])
		self.pod = processed_op.dataframe_args
		self.xl_op_file = XL_WRITE(folder=self.output_path, 
								**processed_op.dataframe_args)
