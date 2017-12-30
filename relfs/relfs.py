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
def load_config_file(file_path):
	try:
		config_file = open(file_path, 'rt')
		return json.load(config_file)
	except IOError as io_error:
		if io_error.errno == os.errno.ENOENT:
			return dict()
		else: raise
#------------------------------------------------------------------------------#
def load_config_files():
	config = dict()
	for file_path in get_repo_config_file_list():
		config.update(load_config_file(file_path))

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
def __existing_repo_names():
	return list(__config().repositories.keys())
#------------------------------------------------------------------------------#
def get_default_arg_parser(
	command, description,
	with_repo_names=False,
	with_file_paths=False,
	existing_repos=False
):
	import argparse

	class __RelfsArgumentParser(argparse.ArgumentParser):
		def __init__(self, *args, **kw):
			argparse.ArgumentParser.__init__(self, *args, **kw)
			with_repo_names=False
			with_file_paths=False

		def process_parsed_options(self, options):
			repos = [x[1:] for x in options.arguments if x[0] == '@']
			files = [x     for x in options.arguments if x[0] != '@']
			if self.with_repo_names:
				options.repositories += repos
			elif len(repos) > 0:
				self.error(
					"unexpected repository name '%s' in argument list" % repos[0]
				)


			if self.with_file_paths:
				options.file_paths += files
			elif len(files) > 0:
				self.error(
					"unexpected file path '%s' in argument list" % files[0]
				)


			options.__dict__.pop("arguments", None)
			return options

		def parse_args(self):
			return self.process_parsed_options(
				argparse.ArgumentParser.parse_args(self)
			)

	argparser = __RelfsArgumentParser(
		prog=command,
		description=description,
		epilog="""
			Copyright (c) Matúš Chochlík.
			Permission is granted to copy, distribute and/or modify this document
			under the terms of the Boost Software License, Version 1.0.
			(See a copy at http://www.boost.org/LICENSE_1_0.txt)
		"""
	)
	argparser.with_repo_names = with_repo_names
	argparser.with_file_paths = with_file_paths

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

	if with_repo_names:
		if existing_repos:
			argparser.add_argument(
				"--repository", "-r",
				nargs='?',
				dest="repositories",
				choices=__existing_repo_names(),
				default=list(),
				action="append"
			)
		else:
			argparser.add_argument(
				"--repository", "-r",
				nargs='?',
				dest="repositories",
				metavar='REPO-NAME',
				default=list(),
				action="append"
			)

	if with_file_paths:
		argparser.add_argument(
			"--file", "-f",
			metavar='FILE-PATH',
			nargs='?',
			dest="file_paths",
			default=list(),
			action="append"
		)

	if with_repo_names or with_file_paths:
		mvar_list = list()
		help_list = list()

		if with_repo_names:
			if existing_repos:
				mvar_list += [
					'@'+x.encode('ascii', 'ignore')
					for x in __existing_repo_names()
				]
			else: mvar_list.append('@repo')
			help_list.append('repository name')

		if with_file_paths:
			mvar_list.append('file-path')
			help_list.append('file path')

		argparser.add_argument(
			"arguments",
			metavar="|".join(mvar_list),
			nargs='*',
			type=str,
			help=" or ".join(help_list)
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
	pass # TODO
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
	def __repr__(self):
		return "<relfs://%(path)s>" % {"path": self.metadata.path}
	#--------------------------------------------------------------------------#
	def __str__(self):
		return "<relfs:%(name)s>" % {"name": self.name}
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
	def get_object_display_name(self, obj_hash):
		return obj_hash #TODO
	#--------------------------------------------------------------------------#
	def set_object_display_name(self, obj_hash, display_name):
		pass # TODO
#------------------------------------------------------------------------------#
def open_repository(repo_name, config = __config()):
	return Repository(repo_name, config)
#------------------------------------------------------------------------------#
class RepositoryFileObject:
	#--------------------------------------------------------------------------#
	def __init__(self, repo, obj_hash):
		self.repo = repo
		self.obj_hash = obj_hash
	#--------------------------------------------------------------------------#
	def __repr__(self):
		return "<relfs://%(repo)s/%(hash)s>" % {
			"repo": self.repo.get_objects_dir_path(),
			"hash": self.obj_hash
		}
	#--------------------------------------------------------------------------#
	def __str__(self):
		return "<relfs:%(repo)s/%(name)s>" % {
			"repo": self.repo.get_name(),
			"name": self.get_display_name()
		}
	#--------------------------------------------------------------------------#
	def get_path_in_repository(self):
		return self.repo.get_object_file_path(self.obj_hash)
	#--------------------------------------------------------------------------#
	def get_display_name(self):
		return self.repo.get_object_display_name(self.obj_hash)
	#--------------------------------------------------------------------------#
	def set_display_name(self, name):
		self.repo.set_object_display_name(self.obj_hash, name)
#------------------------------------------------------------------------------#
