# coding=utf-8
#------------------------------------------------------------------------------#
"""Implements the RelFS entity class."""
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import persistent
from .component import Component
#------------------------------------------------------------------------------#
class EntityBase(persistent.Persistent):
    """Common base class for RelFs persistent entity."""
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._components = BTrees.OOBTree.BTree()
        self._p_changed = True

    #--------------------------------------------------------------------------#
    def has_component(self, component_class):
        """
        Indicates if this entity instance has component
        of the specified component_class.
        """
        assert isinstance(component_class, type)
        assert issubclass(component_class, Component)
        return self._components.has_key(component_class.unique_id())

    #--------------------------------------------------------------------------#
    def get_component(self, component_class):
        """
        If this entity does not have a component of the specified
        component_class, then a new default instance is added.
        Then the component of component_class is returned of this
        entity is returned.
        """
        assert isinstance(component_class, type)
        assert issubclass(component_class, Component)
        try:
            return self._components[component_class.unique_id()]
        except KeyError:
            result = component_class()
            self._components[component_class.unique_id()] = result
            self._p_changed = True
            return result

    #--------------------------------------------------------------------------#
    def find_component(self, component_class):
        """
        Returns the component with the specified component_class,
        if this entity has one, returns None otherwise.
        """
        assert isinstance(component_class, type)
        assert issubclass(component_class, Component)
        try:
            return self._components[component_class.unique_id()]
        except KeyError:
            return None

    #--------------------------------------------------------------------------#
    def find_all_components_by_name(self, *component_names):
        """
        Returns a tuple of components of this entity with the specified
        component class names if this entity has all of them.
        Returns None otherwise.
        """
        try:
            return tuple(self._components[name] for name in component_names)
        except KeyError:
            return None

    #--------------------------------------------------------------------------#
    def all_components(self):
        """
        Yields pairs of type names and instances of all components
        of this entity.
        """
        for name, component in self._components.items():
            yield name, component

    #--------------------------------------------------------------------------#
    def only_components(self, component_names):
        """
        Yields pairs of type names and instances of components with type
        names specified in the component_names list in the this entity.
        """
        for component_name in component_names:
            try:
                yield component_name, self._components[component_name]
            except KeyError:
                pass


#------------------------------------------------------------------------------#
class Entity(EntityBase):
    """Class representing a identifyiable RelFS entity."""
    #--------------------------------------------------------------------------#
    def __init__(self):
        EntityBase.__init__(self)

    #--------------------------------------------------------------------------#
    def add_component(self, some_component):
        """Adds some_component instance to this entity."""
        assert isinstance(some_component, Component)
        self._components[some_component.unique_id()] = some_component
        self._p_changed = True

#------------------------------------------------------------------------------#
class EntityContext(EntityBase):
    """Class representing shared context for RelFS entities."""
    #--------------------------------------------------------------------------#
    def __init__(self):
        EntityBase.__init__(self)
