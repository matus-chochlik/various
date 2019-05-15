# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import mimetypes
from .component import Component
#------------------------------------------------------------------------------#
def get_file_mime_type(os_path):
    try:
        mimetype, encoding = mimetypes.guess_type(os_path)
        if mimetype:
            return tuple(x for x in str(mimetype).split('/'))
    except Exception: pass

#------------------------------------------------------------------------------#
class MimeType(Component):
    #--------------------------------------------------------------------------#
    def __init__(self, mime_type_and_subtype):
        Component.__init__(self)
        self._mime_type_and_subtype = mime_type_and_subtype

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "MimeType"

    #--------------------------------------------------------------------------#
    def public_values(self):
        return {
            "type": self._mime_type_and_subtype[0],
            "subtype": self._mime_type_and_subtype[1]
        }
    #--------------------------------------------------------------------------#
    def has_type(self, name):
        return self._mime_type_and_subtype[0] == name

    #--------------------------------------------------------------------------#
    def has_subtype(self, name):
        return self._mime_type_and_subtype[1] == name

    #--------------------------------------------------------------------------#
    def tie(self):
        return self._mime_type_and_subtype

    #--------------------------------------------------------------------------#
    def __str__(self):
        return "%s/%s" % self.tie()

    #--------------------------------------------------------------------------#
    def __eq__(self, that):
        return self.tie() == that.tie()

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self.tie() < that.tie()

    #--------------------------------------------------------------------------#
    def __hash__(self):
        return hash(self.tie())

#------------------------------------------------------------------------------#
class AllMimeTypes(Component):
    #--------------------------------------------------------------------------#
    def __init__(self):
        Component.__init__(self)
        self._types = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "AllMimeTypes"

    #--------------------------------------------------------------------------#
    def items(self):
        for tree in self._types.values():
            for mime_type_and_subtype in tree.values():
                yield mime_type_and_subtype

    #--------------------------------------------------------------------------#
    def get_mime_type(self, mime_type_and_subtype):
        assert(isinstance(mime_type_and_subtype, tuple))
        return self._get_subtype(
            self._get_type(mime_type_and_subtype),
            mime_type_and_subtype)

    #--------------------------------------------------------------------------#
    def _get_type(self, mime_type_and_subtype):
        try:
            return self._types[mime_type_and_subtype[0]]
        except KeyError:
            result = BTrees.OOBTree.BTree()
            self._types[mime_type_and_subtype[0]] = result
            self._p_changed = True
            return result

    #--------------------------------------------------------------------------#
    def _get_subtype(self, tree, mime_type_and_subtype):
        try:
            return tree[mime_type_and_subtype[1]]
        except KeyError:
            result = MimeType(mime_type_and_subtype)
            tree[mime_type_and_subtype[1]] = result
            self._p_changed = True
            return result

#------------------------------------------------------------------------------#
def add_mime_type(context, entity, mime_type_and_subtype):
    if mime_type_and_subtype is not None:
        all_mt = context.get_component(AllMimeTypes)
        entity.add_component(all_mt.get_mime_type(mime_type_and_subtype))

#------------------------------------------------------------------------------#
def add_file_mime_type(context, entity, os_path):
    add_mime_type(context, entity, get_file_mime_type(os_path))

#------------------------------------------------------------------------------#
def has_mime_type(context, entity, type_name=None, subtype_name=None):
    mime_type = entity.get_component(MimeType)
    if mime_type:
        return (mime_type.has_type(type_name) or type_name is None) and\
            (mime_type.has_subtype(subtype_name) or subtype_name is None)
    return False
#------------------------------------------------------------------------------#
