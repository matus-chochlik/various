# coding=utf-8
#------------------------------------------------------------------------------#
import BTrees.OOBTree
import persistent
from ..objects import User
#------------------------------------------------------------------------------#
class UserRatings(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._ratings = BTrees.OOBTree.BTree()

    #--------------------------------------------------------------------------#
    def add(self, user, rating):
        assert(type(user) == User)
        assert(type(rating) == float)
        assert(0.0 <= rating and rating <= 1.0)
        self._ratings[user] = rating

    def high(self):
        try: return max(self._ratings.values())
        except ValueError: pass

    def low(self):
        try: return min(self._ratings.values())
        except ValueError: pass

    def average(self):
        try: return sum(self._ratings.values()) / len(self._ratings)
        except ZeroDivisionError: pass

#------------------------------------------------------------------------------#

