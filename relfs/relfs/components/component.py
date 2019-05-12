# coding=utf-8
#------------------------------------------------------------------------------#
import persistent
#------------------------------------------------------------------------------#
class Component(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)

    #--------------------------------------------------------------------------#
    @staticmethod
    def _unique_id():
        raise NotImplementedError("relfs component id not implemented")
    #--------------------------------------------------------------------------#
    @staticmethod
    def public_attribs():
        return []
    #--------------------------------------------------------------------------#
    def public_values(self):
        return {
            name: self.__dict__.get("_"+name)
            for name in self.public_attribs()
        }
    #--------------------------------------------------------------------------#

