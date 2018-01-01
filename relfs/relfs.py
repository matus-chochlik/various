# coding=utf-8
#------------------------------------------------------------------------------#
from __future__ import print_function
import os, sys, json, hashlib, resource, shutil
#------------------------------------------------------------------------------#
__version_numbers= (0,1,0)
#------------------------------------------------------------------------------#
class Error(Exception):
	pass
#------------------------------------------------------------------------------#
def _mkdir_p(os_path):
	try: os.makedirs(os_path)
	except OSError as os_error:
		if not(os_error.errno == os.errno.EEXIST and os.path.isdir(os_path)):
			raise
#------------------------------------------------------------------------------#
def system_config_dir_path():
	return os.path.expanduser('/etc/relfs/')
#------------------------------------------------------------------------------#
def user_config_dir_path():
	return os.path.expanduser('~/.config/relfs/')
#------------------------------------------------------------------------------#
def config_types():
	return ['system', 'user']
#------------------------------------------------------------------------------#
def config_dir_paths():
	return [system_config_dir_path(), user_config_dir_path()]
#------------------------------------------------------------------------------#
def config_dir_types_and_paths():
	return dict(zip(config_types(), config_dir_paths()))
#------------------------------------------------------------------------------#
def config_dir_path(config_type):
	return config_dir_types_and_paths()[config_type]
#------------------------------------------------------------------------------#
def __make_repo_config_file_path(config_dir):
	return os.path.join(config_dir, "repositories")
#------------------------------------------------------------------------------#
def repo_config_file_path(config_type):
	return __make_repo_config_file_path(config_dir_path(config_type))
#------------------------------------------------------------------------------#
def repo_config_file_paths():
	return [__make_repo_config_file_path(x) for x in config_dir_paths()]
#------------------------------------------------------------------------------#
def __load_config_content(file_path):
	try:
		config_file = open(file_path, 'rt')
		return json.load(config_file)
	except IOError as io_error:
		if io_error.errno == os.errno.ENOENT:
			return dict()
		else: raise
#------------------------------------------------------------------------------#
def __save_config_content(file_path, content):
	config_file = open(file_path, 'wt')
	json.dump(content, config_file, indent=2)
#------------------------------------------------------------------------------#
class __ConfigStruct(object):
	def __init__(self, entries):
		self.__dict__.update(entries)
#------------------------------------------------------------------------------#
def load_all_configs():
	config = dict()
	for file_path in repo_config_file_paths():
		config.update(__load_config_content(file_path))

	return __ConfigStruct(config)
#------------------------------------------------------------------------------#
def load_config_file(file_path):
	return __ConfigStruct(__load_config_content(file_path))
#------------------------------------------------------------------------------#
def load_config(config_type):
	return load_config_file(repo_config_file_path(config_type))
#------------------------------------------------------------------------------#
def save_config_file(file_path, config):
	assert(isinstance(config, __ConfigStruct))
	__save_config_content(file_path, config.__dict__)
#------------------------------------------------------------------------------#
def save_config(config_type, config):
	return save_config_file(repo_config_file_path(config_type), config)
#------------------------------------------------------------------------------#
__cached_config = None
def __config():
	global __cached_config
	if __cached_config is None:
		__cached_config = load_all_configs()
	return __cached_config
#------------------------------------------------------------------------------#
def __existing_repo_names():
	return list(__config().repositories.keys())
#------------------------------------------------------------------------------#
def make_default_arg_parser(
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
def make_file_hash(file_path):
	hash_obj = hashlib.sha256()
	chunk_size = resource.getpagesize()
	with open(file_path, "rb") as hashed:
		for chunk in iter(lambda: hashed.read(chunk_size), b""):
			hash_obj.update(chunk)
	return hash_obj.hexdigest()
#------------------------------------------------------------------------------#
class Repository(object):
	#--------------------------------------------------------------------------#
	@staticmethod
	def make_default_config(name):
		return dict()
	#--------------------------------------------------------------------------#
	@staticmethod
	def initialize(config_type, name, os_path):
		if os.path.exists(os_path):
			if os.path.isdir(os_path):
				if len(os.listdir(os_path)) > 0:
					raise Error("repository directory '%s' is not empty" % os_path)
			else:
				raise Error("file '%s' exists and is not a directory" % os_path)
		else:
			_mkdir_p(os_path)

		with open(os.path.join(os_path, "config"), "wt") as config_file:
			json.dump(Repository.make_default_config(name), config_file)

		global_config = load_config(config_type)
		global_config.repositories[name] = os_path
		save_config(config_type, global_config)
	#--------------------------------------------------------------------------#
	def __init__(self, name, config):
		self._name = name
		self._metadata = config.repositories[name]
	#--------------------------------------------------------------------------#
	def __repr__(self):
		return "<relfs://%(path)s>" % {"path": self._metadata.path}
	#--------------------------------------------------------------------------#
	def __str__(self):
		return "<relfs:%(name)s>" % {"name": self._name}
	#--------------------------------------------------------------------------#
	def name(self):
		return self._name
	#--------------------------------------------------------------------------#
	def prefix(self):
		return self._metadata["path"]
	#--------------------------------------------------------------------------#
	def objects_dir_path(self):
		return os.path.join(self.prefix(), "objects")
	#--------------------------------------------------------------------------#
	def object_dir_path(self, obj_hash):
		return os.path.join(self.objects_dir_path(), obj_hash[:3])
	#--------------------------------------------------------------------------#
	def object_file_name(self, obj_hash):
		return obj_hash[3:]
	#--------------------------------------------------------------------------#
	def object_file_path(self, obj_hash):
		return os.path.join(
			self.object_dir_path(obj_hash),
			self.object_file_name(obj_hash)
		)
	#--------------------------------------------------------------------------#
	def checkin_file(self, os_path, display_name=None):
		if not display_name:
			display_name = os.path.basename(os_path)

		obj_hash = make_file_hash(os_path)
		dir_path = self.object_dir_path(obj_hash)
		_mkdir_p(dir_path)
		obj_path = os.path.join(dir_path, self.object_file_name(obj_hash))
		shutil.copyfile(os_path, obj_path)
		self.set_object_display_name(obj_hash, display_name)
		return RepositoryFileObject(self, obj_hash)
	#--------------------------------------------------------------------------#
	def object_display_name(self, obj_hash):
		return obj_hash #TODO
	#--------------------------------------------------------------------------#
	def change_object_display_name(self, obj_hash, display_name):
		pass # TODO
#------------------------------------------------------------------------------#
def open_repository(repo_name, config = __config()):
	return Repository(repo_name, config)
#------------------------------------------------------------------------------#
class RepositoryFileObject(object):
	#--------------------------------------------------------------------------#
	def __init__(self, repo, obj_hash):
		self._repo = repo
		self._obj_hash = obj_hash
	#--------------------------------------------------------------------------#
	def __repr__(self):
		return "<relfs://%(repo)s/%(hash)s>" % {
			"repo": self._repo.objects_dir_path(),
			"hash": self._obj_hash
		}
	#--------------------------------------------------------------------------#
	def __str__(self):
		return "<relfs:%(repo)s/%(name)s>" % {
			"repo": self._repo.name(),
			"name": self.display_name()
		}
	#--------------------------------------------------------------------------#
	def path_in_repository(self):
		return self.repo.object_file_path(self.obj_hash)
	#--------------------------------------------------------------------------#
	def display_name(self):
		return self.repo.object_display_name(self.obj_hash)
	#--------------------------------------------------------------------------#
	def change_display_name(self, name):
		self.repo.change_object_display_name(self.obj_hash, name)
#------------------------------------------------------------------------------#
