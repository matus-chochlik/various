# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import fuse
import errno
from .item import RelFuseItem
from .folder import FolderMachinery
#------------------------------------------------------------------------------#
class MountedDirRepoItem(RelFuseItem):
    # --------------------------------------------------------------------------
    def __init__(self, repository, item_source_path):
        RelFuseItem.__init__(self)
        self._repository = repository
        self._source_path = item_source_path
        self._machinery = FolderMachinery(item_source_path)

    # --------------------------------------------------------------------------
    def find_item(self, split_path):
        if not split_path or split_path == ["."]:
            return self
        sub_path = os.path.join(self._source_path, split_path[0])
        if os.path.isdir(sub_path):
            return MountedDirRepoItem(
                self._repository,
                sub_path).find_item(split_path[1:])

    # --------------------------------------------------------------------------
    def _make_filename(self, obj_hash, entity):
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
        names = self._machinery.required_components()
        if names is not None:
            for obj_hash, entity, insts in context.filter_having_by_name(*names):
                if self._machinery.allow_entity(context, entity, *insts):
                    print(self._make_filename(obj_hash, entity))
        else:
            for obj_hash, entity in context.all_objects():
                if self._machinery.allow_entity(context, entity):
                    print(self._make_filename(obj_hash, entity))

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
            mount_source_config.source_path)
#------------------------------------------------------------------------------#
