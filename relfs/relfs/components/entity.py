# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import persistent
from .component import Component
#------------------------------------------------------------------------------#
class EntityBase(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._components = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    def has_component(self, SomeComponent):
        assert(isinstance(SomeComponent, type))
        assert(issubclass(SomeComponent, Component))
        return self._components.has_key(SomeComponent._unique_id())

    #--------------------------------------------------------------------------#
    def get_component(self, SomeComponent):
        assert(isinstance(SomeComponent, type))
        assert(issubclass(SomeComponent, Component))
        try:
            return self._components[SomeComponent._unique_id()]
        except KeyError:
            result = SomeComponent()
            self._components[SomeComponent._unique_id()] = result
            self_p_changed = True
            return result

    #--------------------------------------------------------------------------#
    def find_component(self, SomeComponent):
        assert(isinstance(SomeComponent, type))
        assert(issubclass(SomeComponent, Component))
        try:
            return self._components[SomeComponent._unique_id()]
        except KeyError:
            return None

    #--------------------------------------------------------------------------#
    def find_all_components_by_name(self, *component_names):
        try:
            return tuple(self._components[name] for name in component_names)
        except KeyError:
            return None

    #--------------------------------------------------------------------------#
    def only_components(self, component_names):
        for component_name in component_names:
            try:
                yield component_name, self._components[component_name]
            except KeyError:
                pass


#------------------------------------------------------------------------------#
class Entity(EntityBase):
    #--------------------------------------------------------------------------#
    def __init__(self):
        EntityBase.__init__(self)

    #--------------------------------------------------------------------------#
    def add_component(self, some_component):
        assert(isinstance(some_component, Component))
        self._components[some_component._unique_id()] = some_component
        self_p_changed = True

#------------------------------------------------------------------------------#
class EntityContext(EntityBase):
    #--------------------------------------------------------------------------#
    def __init__(self):
        EntityBase.__init__(self)


