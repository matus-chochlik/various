# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
from .component import Component
#------------------------------------------------------------------------------#
class PictureInfo(Component):
    #--------------------------------------------------------------------------#
    def __init__(self, width, height):
        Component.__init__(self)
        assert(isinstance(width, int))
        assert(isinstance(height, int))
        self._width = width
        self._height= height

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "PictureInfo"

    #--------------------------------------------------------------------------#
    @staticmethod
    def public_attribs():
        return ["width", "height"]

#------------------------------------------------------------------------------#
def add_picture_info(context, entity, info):
    if info is not None:
        entity.add_component(PictureInfo(info[0], info[1]))
#------------------------------------------------------------------------------#

