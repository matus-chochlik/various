# coding=utf-8
#------------------------------------------------------------------------------#
import ZODB, ZODB.FileStorage
import zc.zlibstorage
import BTrees.OOBTree
import transaction
import persistent
from components.entity import EntityContext, Entity
#------------------------------------------------------------------------------#
class FileObject(Entity):
    #--------------------------------------------------------------------------#
    def __init__(self, obj_hash, display_name, extensions):
        Entity.__init__(self)
        self._obj_hash = obj_hash
        self._display_name = display_name
        self._extensions = extensions

    #--------------------------------------------------------------------------#
    def hash(self):
        return self._obj_hash

    #--------------------------------------------------------------------------#
    def display_name(self):
        return self._display_name

    #--------------------------------------------------------------------------#
    def set_display_name(self, display_name):
        self._display_name = display_name

    #--------------------------------------------------------------------------#
    def extensions(self):
        return self._extensions

#------------------------------------------------------------------------------#
class ObjectRoot(EntityContext):
    #--------------------------------------------------------------------------#
    def __init__(self):
        EntityContext.__init__(self)
        self._objects = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    def object_count(self):
        return len(self._objects)

    #--------------------------------------------------------------------------#
    def find_object(self, obj_hash):
        try:
            return self._objects[obj_hash]
        except KeyError:
            pass
    #--------------------------------------------------------------------------#
    def filter_objects(self, unary_predicate):
        for obj in self._objects.values():
            if unary_predicate(obj):
                yield obj

    #--------------------------------------------------------------------------#
    def all_objects(self):
        for obj_hash, obj in self._objects.items():
            yield obj_hash, obj

    #--------------------------------------------------------------------------#
    def filter_having_by_name(self, *component_names):
        for obj_hash, obj in self._objects.items():
            components = obj.find_all_components_by_name(*component_names)
            if components is not None:
                yield (obj_hash, obj, components)

    #--------------------------------------------------------------------------#
    def for_each_object(self, unary_function):
        for obj in self._objects.values():
            unary_function(obj)

    #--------------------------------------------------------------------------#
    def add_file_object_info(self, obj_hash, display_name, extensions):

        try:
            obj = self._objects[obj_hash]
            obj._display_name = display_name
            obj._extensions = extensions
            self._p_changed = True
            return obj
        except KeyError:
            new_obj = FileObject(obj_hash, display_name, extensions)
            self._objects[obj_hash] = new_obj
            self._p_changed = True
            return new_obj

#------------------------------------------------------------------------------#
class Database:
    #--------------------------------------------------------------------------#
    def __init__(self, repo_path, options, read_only):
        import os
        storage_path = os.path.join(repo_path, 'relfs.zodb')

        self._zodb_storage = ZODB.FileStorage.FileStorage(
            storage_path,
            read_only = read_only)
        if options.get("compress", True):
            self._zodb_storage = zc.zlibstorage.ZlibStorage(self._zodb_storage)

        self._zodb_database = ZODB.DB(self._zodb_storage)
        self._zodb_connection = self._zodb_database.open()
        self._zodb_root = self._zodb_connection.root()

        try:
            self._relfs_root = self._zodb_root["relfs"]
        except KeyError:
            self._relfs_root = self._zodb_root["relfs"] = ObjectRoot()

    #--------------------------------------------------------------------------#
    def context(self):
        return self._relfs_root

    #--------------------------------------------------------------------------#
    def commit(self):
        transaction.commit()

#------------------------------------------------------------------------------#
def open_database(repo_path, options, read_only=False):
    return Database(repo_path, options, read_only=read_only)
#------------------------------------------------------------------------------#
def init_database(repo_path, options):
    Database(repo_path, options)
    transaction.commit()
#------------------------------------------------------------------------------#

