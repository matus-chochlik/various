# coding=utf-8
#------------------------------------------------------------------------------#
"""Implements the base class for RelFS Entity components."""
#------------------------------------------------------------------------------#
import persistent
#------------------------------------------------------------------------------#
class Component(persistent.Persistent):
    """Base class for persistent RelFS Entity components."""
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id():
        """Returns a hashable unique component identifier."""
        raise NotImplementedError("relfs component id not implemented")
    #--------------------------------------------------------------------------#
    @staticmethod
    def public_attribs():
        """
        Returns a list of public attributes of the component.
        Usually overriden in derived component classes.
        """
        return []
    #--------------------------------------------------------------------------#
    def public_values(self):
        """
        Returns a dictionary of public attribute values of this component
        instance.
        """
        return {
            name: self.__dict__.get("_"+name)
            for name in self.public_attribs()
        }
    #--------------------------------------------------------------------------#
