# coding=utf-8
#------------------------------------------------------------------------------#
import persistent
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
class Users(persistent.Persistent):
    #--------------------------------------------------------------------------#
    def __init__(self):
        persistent.Persistent.__init__(self)
        self._users = list()
        self._users.append(User("root"))

    #--------------------------------------------------------------------------#
    @staticmethod
    def name(): return "Users"

    #--------------------------------------------------------------------------#
    def find(self, name):
        for user in self._users:
            if user.has_id(user_id):
                return user

#------------------------------------------------------------------------------#

