# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import time
from .component import Component
#------------------------------------------------------------------------------#
class DateTime(Component):
    #--------------------------------------------------------------------------#
    def __init__(self, struct_time):
        Component.__init__(self)
        assert(isinstance(struct_time, time.struct_time))
        self._struct_time = struct_time

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "DateTime"

    #--------------------------------------------------------------------------#
    def __eq__(self, that):
        return self._struct_time == that._struct_time

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self._struct_time < that._struct_time

#------------------------------------------------------------------------------#
def add_date_time(context, entity, struct_time):
    if struct_time is not None:
        entity.add_component(DateTime(struct_time))
#------------------------------------------------------------------------------#
def get_year(context, entity):
    date_time = entity.find_component(DateTime)
    if date_time is not None:
        return date_time._struct_time.tm_year
#------------------------------------------------------------------------------#

