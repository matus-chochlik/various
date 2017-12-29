# coding=utf-8
#------------------------------------------------------------------------------#
from __future__ import print_function
import os, sys, json, hashlib, resource, shutil
#------------------------------------------------------------------------------#
__version_numbers= (0,1,0)
#------------------------------------------------------------------------------#
def __print_error(message, error):
	print(message, file=sys.stderr)
#------------------------------------------------------------------------------#
def _mkdir_p(os_path):
	try: os.makedirs(os_path)
	except OSError as os_error:
		if not(os_error.errno == os.errno.EEXIST and os.path.isdir(os_path)):
			raise
#------------------------------------------------------------------------------#
repository_kinds = ['user', 'system']
#------------------------------------------------------------------------------#
def get_system_repo_config_file_path():
	return os.path.expanduser('/etc/relfs/repositories')
#------------------------------------------------------------------------------#
def get_user_repo_config_file_path():
	return os.path.expanduser('~/.config/relfs/repositories')
#------------------------------------------------------------------------------#
def get_repo_config_file_list():
	return [
		get_system_repo_config_file_path(),
		get_user_repo_config_file_path()
	]
#------------------------------------------------------------------------------#
def load_config_files():
	config = dict()
	for file_path in get_repo_config_file_list():
		try:
			config_file = open(file_path, 'rt')
			config.update(json.load(config_file))
		except IOError as io_error:
			if io_error.errno == os.errno.ENOENT:
				pass
			else: raise

	return config
#------------------------------------------------------------------------------#
def load_config():
	class ConfigStruct:
		def __init__(self, **entries):
			self.__dict__.update(**entries)

	return ConfigStruct(**load_config_files())
#------------------------------------------------------------------------------#
__cached_config = None
def __config():
	global __cached_config
	if __cached_config is None:
		__cached_config = load_config()
	return __cached_config
#------------------------------------------------------------------------------#
def get_default_arg_parser(
	command, description,
	with_repository_names=False
):
	import argparse
	argparser = argparse.ArgumentParser(
		prog=command,
		description=description,
		epilog="""
			Copyright (c) Matúš Chochlík.
			Permission is granted to copy, distribute and/or modify this document
			under the terms of the Boost Software License, Version 1.0.
			(See a copy at http://www.boost.org/LICENSE_1_0.txt)
		"""
	)

	class __IncVerbosity(argparse.Action):
		def __init__(self, **kw):
			argparse.Action.__init__(self, nargs=0, type=int, **kw)

		def __call__(self, parser, options, values, option_string=None):
			options.verbosity += 1

	argparser.add_argument(
		"--version",
		action="version",
		version="%(prog)s relfs-"+".".join([str(x) for x in __version_numbers])
	)

	argparser.add_argument(
		"--verbose", "-v",
		dest="verbosity",
		default=0,
		action="count"
	)

	if with_repository_names:
		argparser.add_argument(
			"--repository", "-r",
			nargs=1,
			dest="repositories",
			choices=__config().repositories,
			default=list(),
			action="append"
		)

	return argparser
#------------------------------------------------------------------------------#
def init_repository(os_path, options):
	try:
		_mkdir_p(os_path)
	except Exception as error:
		__print_error("failed to initialize repository: ", error)
#------------------------------------------------------------------------------#
def remove_repository(os_path, options):
	pass
#------------------------------------------------------------------------------#
def make_file_hash(file_path):
	hash_obj = hashlib.sha256()
	chunk_size = resource.getpagesize()
	with open(file_path, "rb") as hashed:
		for chunk in iter(lambda: hashed.read(chunk_size), b""):
			hash_obj.update(chunk)
	return hash_obj.hexdigest()
#------------------------------------------------------------------------------#
def make_file_repo_path(repo, os_path, config=__config()):
	repo_prefix = config.repositories[repo]["path"]
	file_hash = make_file_hash(os_path)
	return (os.path.join(repo_prefix, "objects", file_hash[:3]), file_hash[3:])
#------------------------------------------------------------------------------#
class Repository:
	#--------------------------------------------------------------------------#
	def __init__(self, name, config):
		self.name = name
		self.metadata = config.repositories[name]
	#--------------------------------------------------------------------------#
	def get_name(self):
		return self.name
	#--------------------------------------------------------------------------#
	def get_prefix(self):
		return self.metadata["path"]
	#--------------------------------------------------------------------------#
	def get_objects_dir_path(self):
		return os.path.join(self.get_prefix(), "objects")
	#--------------------------------------------------------------------------#
	def get_object_dir_path(self, obj_hash):
		return os.path.join(self.get_objects_dir_path(), obj_hash[:3])
	#--------------------------------------------------------------------------#
	def get_object_file_name(self, obj_hash):
		return obj_hash[3:]
	#--------------------------------------------------------------------------#
	def get_object_file_path(self, obj_hash):
		return os.path.join(
			self.get_object_dir_path(obj_hash),
			self.get_object_file_name(obj_hash)
		)
	#--------------------------------------------------------------------------#
	def checkin_file(self, os_path, display_name=None):
		if not display_name:
			display_name = os.path.basename(os_path)

		obj_hash = make_file_hash(os_path)
		dir_path = self.get_object_dir_path(obj_hash)
		_mkdir_p(dir_path)
		obj_path = os.path.join(dir_path, self.get_object_file_name(obj_hash))
		shutil.copyfile(os_path, obj_path)
		self.set_object_display_name(obj_hash, display_name)
		return RepositoryFileObject(self, obj_hash)
	#--------------------------------------------------------------------------#
	def set_object_display_name(self, obj_hash, display_name):
		pass
#------------------------------------------------------------------------------#
def open_repository(repo_name, config = __config()):
	return Repository(repo_name, config)
#------------------------------------------------------------------------------#
class RepositoryFileObject:
	def __init__(self, repo, obj_hash):
		self.repo = repo
		self.obj_hash = obj_hash

	def get_path(self):
		return self.repo.get_object_file_path(self.obj_hash)

	def set_display_name(self, name):
		self.repo.set_object_display_name(obj_hash, name)
#------------------------------------------------------------------------------#
