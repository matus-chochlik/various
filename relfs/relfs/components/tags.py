# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import persistent
#------------------------------------------------------------------------------#
class Tag(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self, label):
        persistent.Persistent.__init__(self)
        self._label = label

    #--------------------------------------------------------------------------#
    def label(self):
        return self._label

    #--------------------------------------------------------------------------#
    def __eq__(self, that):
        return self._label == that._label

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self._label < that._label

#------------------------------------------------------------------------------#
class AllTags(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._tags = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    def get_tag(self, label):
        try:
            return self._tags[label]
        except KeyError:
            result = Tag(label)
            self._tags[label] = result
            self._p_changed = True
            return result

#------------------------------------------------------------------------------#
class Tags(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._tags = set()

    #--------------------------------------------------------------------------#
    def add_tag(self, tag):
        self._tags.add(tag)
        self._p_changed = True

    #--------------------------------------------------------------------------#
    def remove_tag(self, tag):
        self._tags.remove(tag)
        self._p_changed = True

#------------------------------------------------------------------------------#
def add_tags(context, entity, labels):
    tags = entity.get_component(Tags)
    all_tags = context.get_component(AllTags)
    if isinstance(labels, list):
        for label in labels:
            assert(isinstance(label, str))
            tags.add_tag(all_tags.get_tag(label))
    elif isinstance(labels, str):
        tags.add_tag(all_tags.get_tag(labels))

