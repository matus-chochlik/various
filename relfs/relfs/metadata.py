# coding=utf-8
import re
import subprocess
import psycopg2
#------------------------------------------------------------------------------#
_picture_resolution_reg_ex = re.compile("^(\d+)\s*[Xx]\s*(\d+)$")
#------------------------------------------------------------------------------#
def mine_file_mime_type(db_conn, cursor, os_path, obj_path, obj_hash):
    try:
        import mimetypes
        mimetype, encoding = mimetypes.guess_type(os_path)
        if mimetype:
            mimetype = str(mimetype).split('/')

            cursor.execute("""
                SELECT relfs.set_object_mime_type(%s, %s, %s)
            """, (obj_hash, mimetype[0], mimetype[1]))

            db_conn.commit()
    except Exception: pass

#------------------------------------------------------------------------------#
def _process_file_picture_info(db_conn, cursor, obj_hash, attributes):
    width = None
    height = None
    is_picture = False

    for attrib in attributes:
        match = _picture_resolution_reg_ex.match(attrib)
        if match:
            width = int(match.group(1))
            height = int(match.group(2))

    if width and height:
        cursor.execute("""
            SELECT relfs.add_object_picture_info(%s, %s, %s)
        """, (obj_hash, width, height))

        db_conn.commit()
#------------------------------------------------------------------------------#
def mine_file_metadata(db_conn, cursor, os_path, obj_path, obj_hash):
    try:
        file_proc = subprocess.Popen(
            ['file', '-b', os_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, errors = file_proc.communicate()

        attributes = [ x.strip() for x in output.split(",") ]

        _process_file_picture_info(db_conn, cursor, obj_hash, attributes)
    except Exception: pass
#------------------------------------------------------------------------------#
def add_file_metadata(db_conn, cursor, os_path, obj_path, obj_hash):
    mine_file_metadata(db_conn, cursor, os_path, obj_path, obj_hash)
    mine_file_mime_type(db_conn, cursor, os_path, obj_path, obj_hash)
#------------------------------------------------------------------------------#
