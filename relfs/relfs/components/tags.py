# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import persistent
from .component import Component
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
    def __str__(self):
        return self.label()

    #--------------------------------------------------------------------------#
    def __eq__(self, that):
        return self._label == that._label

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self._label < that._label

#------------------------------------------------------------------------------#
class AllTags(Component):
    #--------------------------------------------------------------------------#
    def __init__(self):
        Component.__init__(self)
        self._tags = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "AllTags"

    #--------------------------------------------------------------------------#
    def get_tag(self, label):
        try:
            return self._tags[label]
        except KeyError:
            result = Tag(label)
            self._tags[label] = result
            self._p_changed = True
            return result

    #--------------------------------------------------------------------------#
    def items(self):
        for tag in self._tags.values():
            yield tag

#------------------------------------------------------------------------------#
class Tags(Component):
    #--------------------------------------------------------------------------#
    def __init__(self):
        Component.__init__(self)
        self._tags = set()

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "Tags"

    #--------------------------------------------------------------------------#
    def public_values(self):
        return [tag.label() for tag in self._tags]

    #--------------------------------------------------------------------------#
    def has_tag(self, label):
        for tag in self._tags:
            if tag.label() == label:
                return True
        return False

    #--------------------------------------------------------------------------#
    def add_tag(self, tag):
        self._tags.add(tag)
        self._p_changed = True

    #--------------------------------------------------------------------------#
    def remove_tag(self, label):
        self._tags.symmetric_difference_update(
            tag for tag in self._tags if tag.label() == label)
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

#------------------------------------------------------------------------------#
def has_tag(context, entity, label):
    tags =  entity.find_component(Tags)
    if tags:
        return tags.has_tag(label)

    return False

#------------------------------------------------------------------------------#
