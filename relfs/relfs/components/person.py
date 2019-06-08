# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
from .component import Component
#------------------------------------------------------------------------------#
class Person(Component):
    #--------------------------------------------------------------------------#
    def __init__(self, moniker, first_name, middle_name, family_name):

        Component.__init__(self)
        self._moniker = moniker
        self._first_name = first_name
        self._middle_name = middle_name
        self._family_name = family_name

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "Person"

    #--------------------------------------------------------------------------#
    def has_moniker(self, moniker):
        return self._moniker == moniker

    #--------------------------------------------------------------------------#
    @staticmethod
    def public_attribs():
        return ["moniker", "first_name", "middle_name", "family_name"]

#------------------------------------------------------------------------------#
class Persons(Component):
    #--------------------------------------------------------------------------#
    def __init__(self):
        Component.__init__(self)
        self._persons = list()

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "Persons"

    #--------------------------------------------------------------------------#
    def find(self, moniker):
        for person in self._persons:
            if person.moniker(moniker):
                return person

#------------------------------------------------------------------------------#
def add_person(
    context,
    moniker,
    first_name = None,
    middle_name = None,
    family_name = None):
    if moniker is not None:
        context.add_component(
            Person(
                moniker,
                first_name,
                middle_name,
                family_name))
#------------------------------------------------------------------------------#

