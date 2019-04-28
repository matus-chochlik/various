# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import persistent
import mimetypes
#------------------------------------------------------------------------------#
def get_file_mime_type(os_path):
    try:
        mimetype, encoding = mimetypes.guess_type(os_path)
        if mimetype:
            return tuple(x for x in str(mimetype).split('/'))
    except Exception: pass

    return ("application", "octet-stream")

#------------------------------------------------------------------------------#
class MimeType(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self, mime_type_and_subtype):
        persistent.Persistent.__init__(self)
        self._mime_type_and_subtype = mime_type_and_subtype

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
    def __eq__(self, that):
        return self.tie() == that.tie()

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self.tie() < that.tie()

    #--------------------------------------------------------------------------#
    def __hash__(self):
        return hash(self.tie())


#------------------------------------------------------------------------------#
class AllMimeTypes(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._types = BTrees.OOBTree.BTree()

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
