# coding=utf-8
#------------------------------------------------------------------------------#
import os
import time
import datetime
import getpass
import psycopg2
#------------------------------------------------------------------------------#
class DatabaseObjectTable(object):
    #--------------------------------------------------------------------------#
    def __init__(self, name, key_column_name, mutable, associative):
        self.name = name
        self.mutable = mutable
        self.associative = associative
        self.key_column_name = key_column_name
        self.key_column_names = set([key_column_name])
    #--------------------------------------------------------------------------#
    def add_key_column( self, key_column_name):
        self.key_column_names.add(key_column_name)

#------------------------------------------------------------------------------#
class DatabaseComponentAttribute(object):
    #--------------------------------------------------------------------------#
    def __init__(self, name, table, column_name):
        self.name = name
        self.table = table
        self.column_name = column_name

#------------------------------------------------------------------------------#
class DatabaseObjectComponent(object):
    #--------------------------------------------------------------------------#
    def __init__(self, name):
        self.name = name
        self.attributes = {}
    #--------------------------------------------------------------------------#
    def add_attribute(self, attribute_name, table, column_name):
        self.attributes[attribute_name] = DatabaseComponentAttribute(
            attribute_name,
            table,
            column_name
        )

#------------------------------------------------------------------------------#
class DatabaseUnmodifiedValue(object):
    #--------------------------------------------------------------------------#
    def __init__(self):
        pass
#------------------------------------------------------------------------------#
class DatabaseComponentModification(object):
    #--------------------------------------------------------------------------#
    def __init__(self, parent, component):
        self._parent = parent
        self._component = component
        self._reset()
    #--------------------------------------------------------------------------#
    def _reset(self):
        for name, attribute in self._component.attributes.items():
            if attribute.table.mutable:
                self.__dict__[name] = DatabaseUnmodifiedValue()
    #--------------------------------------------------------------------------#
    def _adjust_value(self, value):
        if type(value) is time.struct_time:
            value = datetime.datetime.fromtimestamp(time.mktime(value))

        return value
    #--------------------------------------------------------------------------#
    def _sql_args(self, key_value):
        modified = {}
        mod_tables = {}
        for name, attribute in self._component.attributes.items():
            if attribute.table.mutable:
                attr_value = self.__dict__[name]
                if type(attr_value) is not DatabaseUnmodifiedValue:
                    modified[name] = self._adjust_value(attr_value)
                    ac_name = (name, attribute.column_name)
                    try:
                        mod_tables[attribute.table.name] += [ac_name]
                    except KeyError:
                        mod_tables[attribute.table.name] = [ac_name]

        if len(mod_tables) > 0:
            modified["_key"] = key_value
            for table_name, ac_names in mod_tables.items():
                table = self._parent._tables[table_name]
                ack_names = [("_key", table.key_column_name)] + ac_names
                sql = "INSERT INTO relfs.%s (%s) VALUES(%s) " % (
                    table_name,
                    ",".join([cn for an, cn in ack_names]),
                    ",".join(["%%(%s)s" % an for an, cn in ack_names])
                )
                sql += "ON CONFLICT(%s) DO " % (
                    ",".join(table.key_column_names)
                )
                sql += "UPDATE SET %s" % (
                    ",".join(["%s = %%(%s)s" % (cn, an) for an, cn in ac_names])
                )



            print(sql, modified)
            yield (sql, modified)

#------------------------------------------------------------------------------#
class DatabaseObjectModification(object):
    #--------------------------------------------------------------------------#
    def __init__(self, db_conn, cursor, obj_hash, tables, components):
        self._db_conn = db_conn
        self._cursor = cursor
        self._obj_hash = obj_hash
        self._tables = tables
        self._components = components

        self._cursor.execute("""SELECT relfs.get_file_object(%s)""", (obj_hash,))
        self._obj_id = self._cursor.fetchone()[0]
        for name, component in self._components.items():
            self.__dict__[name] = DatabaseComponentModification(self, component)
    #--------------------------------------------------------------------------#
    def apply(self):
        for name, component in self._components.items():
            for modification in self.__dict__[name]._sql_args(self._obj_id):
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

        self._tables = {}
        self._components = {}

        cursor = self._db_conn.cursor()

        # load table metadata
        cursor.execute("""
            SELECT table_name, key_column_name, mutable, associative
            FROM relfs.meta_table
        """)
        row = cursor.fetchone()
        while row:
            table_name, key_column_name, mutable, associative = row
            table = DatabaseObjectTable(
                table_name,
                key_column_name,
                mutable,
                associative
            )
            self._tables[table_name] = table
            row = cursor.fetchone()

        # load table key metadata
        cursor.execute("""
            SELECT table_name, key_column_name
            FROM relfs.meta_table_key
        """)
        row = cursor.fetchone()
        while row:
            table_name, key_column_name = row
            self._tables[table_name].add_key_column(key_column_name)
            row = cursor.fetchone()

        # load component metadata
        cursor.execute("""
            SELECT component_name
            FROM relfs.meta_component
        """)
        row = cursor.fetchone()
        while row:
            (component_name,) = row
            component = DatabaseObjectComponent(component_name)
            self._components[component_name] = component
            row = cursor.fetchone()

        # load component attribute metadata
        cursor.execute("""
            SELECT
                table_name,
                column_name,
                component_name,
                attribute_name,
                foreign_table_name
            FROM relfs.meta_component_attribute
        """)
        row = cursor.fetchone()
        while row:
            table_name, \
            column_name, \
            component_name, \
            attribute_name, \
            foreign_table_name = row
            self._components[component_name].add_attribute(
                attribute_name,
                self._tables[table_name],
                column_name)
            row = cursor.fetchone()

        # done loading metadata
        cursor.close()
    #--------------------------------------------------------------------------#
    def set_object(self, obj_hash):
        return DatabaseObjectModification(
            self._db_conn,
            self._db_conn.cursor(),
            obj_hash,
            self._tables,
            self._components
        )

#------------------------------------------------------------------------------#
def open_database(repo_config):
    return Database(repo_config)
#------------------------------------------------------------------------------#

