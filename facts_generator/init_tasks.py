
""" ''' # Parse from SH RUN, SH INT STATUS, SH LLDP NEIGH -> Cis # ''' """
""" ''' # Parse from sh config, sh int desc, sh lldp neigh -> Jun # ''' """
# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from nettoolkit import Juniper, IO, STR

from .dev_juniper import JuniperTasks
from .dev_cisco import CiscoTasks

# ---------------------------------------------------------------------------- #
# Initialize Tasks Operation
# ---------------------------------------------------------------------------- #

class InitTask():


	def __init__(self, hostname=None, files=None):
		self.hostname = hostname 					# depricated: was used in netNinja
		self.files = files
		# self.file_list = IO.file_to_list(file)
		self.create_commands_list()
		self.set_hostname_of_device()
		# self.split_commands_lists()
		self.detect_config_type()
		self.execute_vendor_tasks()

	def create_commands_list(self):
		self.run_list = IO.file_to_list(self.files['config'])
		self.lldp_list = IO.file_to_list(self.files['neighbour'])
		self.int_status_list = IO.file_to_list(self.files['interfaces'])
		# ... Add more as and when add new commands
		self.cmds = {
				# Cisco Commands
				'ter len 0': '',
				'sh run': self.run_list, 
				'sh lldp nei': self.lldp_list,
				'sh int status': self.int_status_list,

				# Juniper Commands
				'show configuration | no-more': self.run_list, 
				'show lldp neighbors | no-more': self.lldp_list, 
				'show interfaces descriptions | no-more': self.int_status_list,
				}

	def set_hostname_of_device(self):
		for line in self.run_list:
			if (line.lstrip().startswith("hostname ") or
				line.lstrip().startswith("host-name ") or
				line.lstrip().startswith("set system hostname ") or
				line.lstrip().startswith("set system host-name ")
				):
				self.hostname = line.split()[-1]

	def detect_config_type(self):
		self.dev_type = None
		for line in self.run_list:
			if STR.is_blank_line(line): continue
			if line.lstrip()[0] == "!":
				self.dev_type = 'cisco'
				break
			if line.lstrip()[0] == "#":
				self.dev_type = 'juniper'
				break
		return self.dev_type

	def execute_vendor_tasks(self):
		if self.dev_type == 'cisco':
			self.tasks = CiscoTasks(run_list=self.run_list, 
									lldp_list=self.lldp_list, 
									int_status_list=self.int_status_list)
			self.tasks.get_aaza()

		elif self.dev_type == 'juniper':
			J = Juniper(input_file=self.files['config'])
			set_output = J.convert_to_set()
			self.tasks = JuniperTasks(run_list=set_output, 
									lldp_list=self.lldp_list,
									int_status_list=self.int_status_list)
			self.tasks.get_aaza()

# ---------------------------------------------------------------------------- #

