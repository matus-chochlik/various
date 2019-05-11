# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
from .item import RelFuseItem
from .folder import get_folder_machinery
#------------------------------------------------------------------------------#
class MountedDirRepoItem(RelFuseItem):
    # --------------------------------------------------------------------------
    def __init__(self, repository, source_root, split_path):
        RelFuseItem.__init__(self)
        self._repository = repository
        self._source_root = source_root
        self._split_path = split_path
        self._source_path = os.path.join(source_root, *split_path)
        self._machinery = get_folder_machinery(source_root, split_path)

    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path or split_path == ["."]:
            return self
        sub_path = os.path.join(self._source_path, split_path[0])
        if os.path.isdir(sub_path):
            return MountedDirRepoItem(
                self._repository,
                self._source_root,
                self._split_path+
                split_path[:1]).find_item(split_path[1:])

    # --------------------------------------------------------------------------
    def _make_filename(self, obj_hash, context, entity):
        # TODO: nicer filename
        return str(obj_hash)

    # --------------------------------------------------------------------------
    def readdir(self, fh):
        yield ".."
        yield "."

        for name in os.listdir(self._source_path):
            if os.path.isdir(os.path.join(self._source_path, name)):
                if not name.startswith('.'):
                    yield name

        context = self._repository.context()
        for obj_hash, entity in self._machinery.allowed_entities(context):
            print(self._make_filename(obj_hash, context, entity))

    # --------------------------------------------------------------------------
    def access(self, mode):
        if mode & os.X_OK:
            return 0
        return RelFuseItem.access(self, mode)

    # --------------------------------------------------------------------------
    def _get_mode(self):
        return 0o40550

#------------------------------------------------------------------------------#
class MountedDirRepo(MountedDirRepoItem):
    # --------------------------------------------------------------------------
    def __init__(self, repository, mount_source_config):
        MountedDirRepoItem.__init__(
            self,
            repository,
            mount_source_config.source_path, [])
#------------------------------------------------------------------------------#
