# coding=utf-8
#------------------------------------------------------------------------------#
import os
import sys
import json
import shutil
import hashlib
import resource
#------------------------------------------------------------------------------#
from .config import load_config, save_config, __config
from .error import RelFsError
#------------------------------------------------------------------------------#
_version_numbers= (0,1,0)
#------------------------------------------------------------------------------#
def _mkdir_p(os_path):
	try: os.makedirs(os_path)
	except OSError as os_error:
		if not(os_error.errno == os.errno.EEXIST and os.path.isdir(os_path)):
			raise
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
					raise RelFsError("repository directory '%s' is not empty" % os_path)
			else:
				raise RelFsError("file '%s' exists and is not a directory" % os_path)
		else:
			_mkdir_p(os_path)

		with open(os.path.join(os_path, "config"), "wt") as config_file:
			json.dump(Repository.make_default_config(name), config_file)

		global_config = load_config(config_type)
		global_config.repositories[name] = {"path": os_path}
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

		try:
			obj_hash = make_file_hash(os_path)
			dir_path = self.object_dir_path(obj_hash)
			_mkdir_p(dir_path)
			obj_path = os.path.join(dir_path, self.object_file_name(obj_hash))
			shutil.copyfile(os_path, obj_path)
			self.change_object_display_name(obj_hash, display_name)
			return RepositoryFileObject(self, obj_hash)
		except IOError as io_error:
			raise RelFsError(str(io_error))
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
