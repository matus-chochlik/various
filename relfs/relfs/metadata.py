# coding=utf-8
import mimetypes
import psycopg2
#------------------------------------------------------------------------------#
def store_file_mime_type(db_conn, cursor, os_path, obj_path, obj_hash):
    try:
        mimetype, encoding = mimetypes.guess_type(os_path)
        if mimetype:
            mimetype = str(mimetype).split('/')

            cursor.execute("""
                SELECT relfs.store_object_mime_type(%s, %s, %s)
            """, (obj_hash, mimetype[0], mimetype[1]))

            db_conn.commit()
    except Exception as bla: print(bla)

#------------------------------------------------------------------------------#
def add_file_metadata(db_conn, cursor, os_path, obj_path, obj_hash):
    store_file_mime_type(db_conn, cursor, os_path, obj_path, obj_hash)
#------------------------------------------------------------------------------#
