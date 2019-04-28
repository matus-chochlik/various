# coding=utf-8
#------------------------------------------------------------------------------#
import ZODB, ZODB.FileStorage
import zc.zlibstorage
import BTrees.OOBTree
import transaction
import persistent
import mimetypes
#------------------------------------------------------------------------------#
class User(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self, user_id):
        persistent.Persistent.__init__(self)
        self._user_id = user_id

    #--------------------------------------------------------------------------#
    def has_id(self, some_id):
        return self._user_id == some_id

    #--------------------------------------------------------------------------#
    def __eq__(self, that):
        return self._user_id == that._user_id

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self._user_id < that._user_id

#------------------------------------------------------------------------------#
class MimeType(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self, mime_type, mime_subtype):
        persistent.Persistent.__init__(self)
        self._type = mime_type
        self._subtype = mime_subtype

    #--------------------------------------------------------------------------#
    def tie(self):
        return (self._type, self._subtype)

    #--------------------------------------------------------------------------#
    def __eq__(self, that):
        return self.tie() == that.tie()

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self.tie() < that.tie()

#------------------------------------------------------------------------------#
class Entity(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._components = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    def has_component(self, name):
        return self._components.has_key(name);

    #--------------------------------------------------------------------------#
    def add_component(self, component):
        assert(isinstance(component, persistent.Persistent))
        self._components[type(component)] = component
        self_p_changed = True

    #--------------------------------------------------------------------------#
    def get_all_components(self, *args):
        try:
            return tuple(self._components[cls] for cls in args)
        except KeyError:
            return None

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
class ObjectRoot(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._users = list()
        self._users.append(User("root"))
        self._mime_types = BTrees.OOBTree.BTree()
        self._objects = list()

    #--------------------------------------------------------------------------#
    def find_user(self, user_id):
        for user in self._users:
            if user.has_id(user_id):
                return user

    #--------------------------------------------------------------------------#
    def object_count(self):
        return len(self._objects)

    #--------------------------------------------------------------------------#
    def filter_objects(self, unary_predicate):
        for obj in self._objects:
            if unary_predicate(obj):
                yield obj
    #--------------------------------------------------------------------------#
    @staticmethod
    def _return_repacked(*args):
        return args

    #--------------------------------------------------------------------------#
    def filter_having(self, *args):
        for obj in self._objects:
            components = obj.get_all_components(*args)
            if components is not None:
                yield self._return_repacked(obj, *components)

    #--------------------------------------------------------------------------#
    def for_each_object(self, unary_function):
        for obj in self._objects:
            unary_function(obj)

    #--------------------------------------------------------------------------#
    def add_file_object_info(
        self,
        obj_hash,
        display_name,
        extensions,
        mime_type):

        new_obj = FileObject(obj_hash, display_name, extensions)
        self._objects.append(new_obj)
        self._p_changed = True
        return new_obj

#------------------------------------------------------------------------------#
class Database:
    #--------------------------------------------------------------------------#
    def __init__(self, repo_path, options):
        import os
        storage_path = os.path.join(repo_path, 'relfs.zodb')

        self._zodb_storage = ZODB.FileStorage.FileStorage(storage_path)
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
    def root(self):
        return self._relfs_root
#------------------------------------------------------------------------------#
def open_database(repo_path, options):
    return Database(repo_path, options)
#------------------------------------------------------------------------------#
def init_database(repo_path, options):
    Database(repo_path, options)
    transaction.commit()
#------------------------------------------------------------------------------#

