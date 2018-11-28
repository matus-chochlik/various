# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import datetime
import getpass
import psycopg2
#------------------------------------------------------------------------------#
class DatabaseObjectComponent(object):
    #--------------------------------------------------------------------------#
    def __init__(self, key_name, table_name):
        self._table_name = table_name
        self.attributes = {}
    #--------------------------------------------------------------------------#
    def add_attribute(self, attribute_name, column_name, mutable):
        self.attributes[attribute_name] = (column_name, mutable)

#------------------------------------------------------------------------------#
class DatabaseUnmodifiedValue(object):
    #--------------------------------------------------------------------------#
    def __init__(self):
        pass
#------------------------------------------------------------------------------#
class DatabaseComponentModification(object):
    #--------------------------------------------------------------------------#
    def __init__(self, component):
        self._component = component
        self._reset()
    #--------------------------------------------------------------------------#
    def _reset(self):
        for name, info in self._component.attributes.items():
            if info[1]:
                self.__dict__[name] = DatabaseUnmodifiedValue()
    #--------------------------------------------------------------------------#
    def _adjust_value(self, value):
        if type(value) is time.struct_time:
            value = datetime.datetime.fromtimestamp(time.mktime(value))

        return value
    #--------------------------------------------------------------------------#
    def _sql_args(self, obj_id):
        modified = {}
        for name, info in self._component.attributes.items():
            if info[1]:
                attr_value = self.__dict__[name]
                if type(attr_value) is not DatabaseUnmodifiedValue:
                    modified[name] = self._adjust_value(attr_value)

        if len(modified) > 0:
            sql = "UPDATE relfs.%s SET" % self._component._table_name
            first = True
            for name in modified:
                sql += "%s%s = %%(%s)s" % (
                    " " if first else ", ",
                    self._component.attributes[name][0],
                    name
                )
                first = False
            sql += " WHERE object_id = %(obj_id)s"

            modified["obj_id"] = obj_id

            return (sql, modified)

        return None

#------------------------------------------------------------------------------#
class DatabaseObjectModification(object):
    #--------------------------------------------------------------------------#
    def __init__(self, db_conn, cursor, obj_hash, components):
        self._db_conn = db_conn
        self._cursor = cursor
        self._obj_hash = obj_hash
        self._components = components

        self._cursor.execute("""SELECT relfs.get_file_object(%s)""", (obj_hash,))
        self._obj_id = self._cursor.fetchone()[0]
        for name, component in self._components.items():
            self.__dict__[name] = DatabaseComponentModification(component)
    #--------------------------------------------------------------------------#
    def apply(self):
        for name, component in self._components.items():
            modification = self.__dict__[name]._sql_args(self._obj_id)
            if modification:
                mod_sql, mod_args = modification
                self._cursor.execute(mod_sql, mod_args)
                self._db_conn.commit()
#------------------------------------------------------------------------------#
class Database(object):
    #--------------------------------------------------------------------------#
    def __init__(self, repo_config):
        user = getpass.getuser()
        if repo_config.get("local_db", False):
            self._db_conn = psycopg2.connect(
                database = repo_config.get("database", user)
            )
        else:
            self._db_conn = psycopg2.connect(
                database = repo_config.get("database", user),
                user = repo_config.get("db_user", user),
                host = repo_config.get("db_host", "localhost"),
                port = repo_config.get("db_port", 5432)
            )

        self._object_components = {}

        cursor = self._db_conn.cursor()
        cursor.execute("""
            SELECT
                key_name,
                table_name,
                foreign_table_name,
                column_name,
                component_name,
                attribute_name,
                mutable
            FROM relfs.meta_component_attribute
        """)
        row = cursor.fetchone()
        while row:
            key_name, \
            table_name, \
            foreign_table_name, \
            column_name, \
            component_name, \
            attrib_name, \
            mutable = row
            try:
                component = self._object_components[component_name]
            except KeyError:
                component = DatabaseObjectComponent(key_name, table_name)
                self._object_components[component_name] = component

            component.add_attribute(attrib_name, column_name, mutable)

            row = cursor.fetchone()
        cursor.close()
    #--------------------------------------------------------------------------#
    def set_object(self, obj_hash):
        return DatabaseObjectModification(
            self._db_conn,
            self._db_conn.cursor(),
            obj_hash,
            self._object_components
        )

#------------------------------------------------------------------------------#
def open_database(repo_config):
    return Database(repo_config)
#------------------------------------------------------------------------------#

