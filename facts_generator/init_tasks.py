
""" ''' # Parse from SH RUN, SH INT STATUS, SH LLDP NEIGH -> Cis # ''' """
""" ''' # Parse from sh config, sh int desc, sh lldp neigh -> Jun # ''' """
# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
from nettoolkit import JSet, IO, STR

from .dev_juniper import JuniperTasks
from .dev_cisco import CiscoTasks

# ---------------------------------------------------------------------------- #
# Initialize Tasks Operation
# ---------------------------------------------------------------------------- #

class InitTask():


	def __init__(self, files=None):
		self.files = files
		if isinstance(files, dict): self.create_commands_list_from_dict_of_files()
		if isinstance(files, str): self.create_commands_list_from_a_file()
		self.set_hostname_of_device()
		self.detect_config_type()
		self.execute_vendor_tasks()

	def create_commands_list_from_dict_of_files(self):
		self.run_list = IO.file_to_list(self.files['config'])
		self.lldp_list = IO.file_to_list(self.files['neighbour'])
		self.int_status_list = IO.file_to_list(self.files['interfaces'])
		self.add_output_lists_to_cmd_dict()

	def create_commands_list_from_a_file(self):
		(self.run_list, self.lldp_list, self.int_status_list) = ([''], [''], [''])
		self.add_output_lists_to_cmd_dict()
		prefix = "# output for command: "
		prefix_len = len(prefix)
		cmd = None
		with open(self.files, 'r') as f:
			lines = f.readlines()
		for line in lines:
			if line.startswith(prefix):
				cmd = line[prefix_len:].strip()
				if not self.cmds.get(cmd): cmd=None
			if not cmd: continue
			if line.startswith(("#", "!")): continue
			self.cmds[cmd].append(line)

	def add_output_lists_to_cmd_dict(self):
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
			J = JSet(input_list=self.run_list)
			J.to_set
			set_output = J.output
			self.tasks = JuniperTasks(run_list=set_output, 
									lldp_list=self.lldp_list,
									int_status_list=self.int_status_list)
			self.tasks.get_aaza()

# ---------------------------------------------------------------------------- #

