# coding=utf-8
#------------------------------------------------------------------------------#
import persistent
from .component import Component
from .users import User, Users
#------------------------------------------------------------------------------#
class UserRatings(Component):
    #--------------------------------------------------------------------------#
    def __init__(self):
        Component.__init__(self)
        self._ratings = list()

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "UserRatings"

    #--------------------------------------------------------------------------#
    def add(self, user, rating):
        assert(type(user) == User)
        assert(type(rating) == float)
        assert(0.0 <= rating and rating <= 1.0)

        self._ratings = [(u, r) for u, r in self._ratings if u != user]
        self._ratings.append((user, rating))
        self._p_changed = True

    def remove(self, user):
        assert(type(user) == User)
        self._ratings = [(u, r) for u, r in self._ratings if u != user]
        self._p_changed = True

    def values(self):
        for u, r in self._ratings:
            yield r

    def high(self):
        try: return max(self.values())
        except ValueError: pass

    def low(self):
        try: return max(self.values())
        except ValueError: pass

    def average(self):
        try: return sum(self.values()) / len(self._ratings)
        except ZeroDivisionError: pass

#------------------------------------------------------------------------------#

