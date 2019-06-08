# coding=utf-8
#------------------------------------------------------------------------------#
import persistent
from .component import Component
#------------------------------------------------------------------------------#
class User(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self, user_id):
        persistent.Persistent.__init__(self)
        self._user_id = user_id

    #--------------------------------------------------------------------------#
    def has_id(self, some_id):
        return self._user_id == some_id

    #--------------------------------------------------------------------------#
    def __eq__(self, that):
        return self._user_id == that._user_id

    #--------------------------------------------------------------------------#
    def __lt__(self, that):
        return self._user_id < that._user_id

#------------------------------------------------------------------------------#
class Users(Component):
    #--------------------------------------------------------------------------#
    def __init__(self):
        Component.__init__(self)
        self._users = list()
        self._users.append(User("root"))

    #--------------------------------------------------------------------------#
    @staticmethod
    def unique_id(): return "Users"

    #--------------------------------------------------------------------------#
    def find(self, user_id):
        for user in self._users:
            if user.has_id(user_id):
                return user

#------------------------------------------------------------------------------#

