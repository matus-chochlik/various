# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import persistent
#------------------------------------------------------------------------------#
class EntityBase(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._components = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    def has_component(self, name):
        return self._components.has_key(name);

    #--------------------------------------------------------------------------#
    def get_component(self, Component):
        assert(isinstance(Component, type))
        try:
            return self._components[Component]
        except KeyError:
            result = Component()
            self._components[Component] = result
            self_p_changed = True
            return result

    #--------------------------------------------------------------------------#
    def find_component(self, Component):
        assert(isinstance(Component, type))
        try:
            return self._components[Component]
        except KeyError:
            return None

#------------------------------------------------------------------------------#
class Entity(EntityBase):
    #--------------------------------------------------------------------------#
    def __init__(self):
        EntityBase.__init__(self)

    #--------------------------------------------------------------------------#
    def add_component(self, component):
        assert(isinstance(component, persistent.Persistent))
        self._components[type(component)] = component
        self_p_changed = True

    #--------------------------------------------------------------------------#
    def find_all_components(self, *args):
        try:
            return tuple(self._components[cls] for cls in args)
        except KeyError:
            return None

#------------------------------------------------------------------------------#
class EntityContext(EntityBase):
    #--------------------------------------------------------------------------#
    def __init__(self):
        EntityBase.__init__(self)


