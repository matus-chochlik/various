# coding=utf-8
#------------------------------------------------------------------------------#
import os
import imp
#------------------------------------------------------------------------------#
class DirMachinery(object):
    # --------------------------------------------------------------------------
    def __init__(self, source_path):
        self._source_path = source_path
        self._required_components = None
        self._filter_function = None
        
        search_path = os.path.join(self._source_path, ".relfs")
        self._try_import_filter_py(search_path)
    # --------------------------------------------------------------------------
    def _try_import_filter_py(self, search_path):
        imp.acquire_lock()
        try:
            filter_py = imp.load_source(
                "relfs.filter",
                os.path.join(search_path, "filter.py"))

            self._required_components = filter_py.required_components()
            if self._required_components is not None:
                assert(type(self._required_components) == tuple)
                for x in self._required_components:
                    assert(type(x) == str)

            self._filter_function = filter_py.allow_entity
        except IOError:
            # TODO: report error (if not ENOENT)
            pass
        except ImportError:
            # TODO: report error
            pass
        except SyntaxError:
            # TODO: report error
            pass
        except AssertionError:
            # TODO: report error
            pass
        imp.release_lock()

    # --------------------------------------------------------------------------
    def allowed_entities(self, context):
        names = self._required_components
        if names is not None:
            for obj_hash, entity, insts in context.filter_having_by_name(*names):
                if self._allow_entity(context, entity, *insts):
                    yield obj_hash, entity
        else:
            for obj_hash, entity in context.all_objects():
                if self._allow_entity(context, entity):
                    yield obj_hash, entity

    # --------------------------------------------------------------------------
    def _allow_entity(self, context, entity, *components):
        if self._filter_function:
            return self._filter_function(context, entity, *components)
        return False
#------------------------------------------------------------------------------#
def get_folder_machinery(source_root, split_path):
    return DirMachinery(os.path.join(source_root, *split_path))
#------------------------------------------------------------------------------#

