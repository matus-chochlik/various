# coding=utf-8
import re
import time
import datetime
import subprocess
import psycopg2
#------------------------------------------------------------------------------#
def mine_file_mime_type(db_obj, os_path, obj_path, obj_hash):
    try:
        import mimetypes
        mimetype, encoding = mimetypes.guess_type(os_path)
        if mimetype:
            mimetype = str(mimetype).split('/')

            db_obj.mime.type = mimetype[0]
            db_obj.mime.subtype = mimetype[1]
            db_obj.apply()

    except Exception: pass
#------------------------------------------------------------------------------#
def _tokenize_file_info_string(file_info):
    tokens = [str()]

    prev_eq = False

    for c in file_info:
        if c.isspace():
            tokens += [str()]
        elif c in [',', '=', '[', ']', '(', ')']:
            tokens += [c]
            tokens += [str()]
            prev_eq = c == '='
        elif c == ':' and not prev_eq:
            tokens += ['=']
            tokens += [str()]
            prev_eq = False
        else:
            tokens[-1] += c

    return [ x for x in tokens if x ]
#------------------------------------------------------------------------------#
def _rejoin_file_info_strings(items):
    result = []
    temp = []

    def process_previous(tmp, res):
        if tmp:
            if len(tmp) == 2:
                try:
                    value = eval(tmp[1])
                    res.append(tmp[0])
                    res.append('=')
                    res.append(value)
                    return []
                except:
                    res.append(' '.join(tmp))
            elif len(tmp) == 1:
                res.append(tmp[0])
            else:
                res.append(' '.join(tmp))
        return []

    prev_eq = False
    for item in items:
        if type(item) is list:
            temp = process_previous(temp, result)
            result.append(_rejoin_file_info_strings(item))
        elif item in [',', '=']:
            temp = process_previous(temp, result)
            result.append(item)
            prev_eq = item == '='
        elif item == ':' and not prev_eq:
            temp = process_previous(temp, result)
            result.append(item)
            prev_eq = False
        else:
            temp.append(item)

    process_previous(temp, result)

    return result
#------------------------------------------------------------------------------#
def _separate_file_info_items(items):

    separated = []
    temp = []

    for item in items:
        if item == ',':
            if temp: separated.append(temp)
            temp = []
        elif type(item) is list:
            temp.append(_separate_file_info_items(item))
        else:
            temp.append(item)

    if temp: separated.append(temp)

    result = []

    for item in separated:
        if len(item) == 1:
            result.append(item[0])
        elif len(item) > 1 and item[1] == '=':
            if len(item) == 3:
                try:
                    result.append((item[0], eval(item[2])))
                except:
                    result.append((item[0], item[2]))
            else:
                try:
                    result.append((item[0], [eval(x) for x in item[2:]]))
                except:
                    result.append((item[0], item[2:]))
        else:
            result.append(item)

    return result
#------------------------------------------------------------------------------#
def _structure_file_info_string(tokens):

    nested = []
    stack = [nested]

    for token in tokens:
        if token in ['[', '(']:
            stack.append([])
        elif token in [']', ')']:
            nested.append(stack[-1])
            stack.pop()
        else:
            stack[-1].append(token)

    return _separate_file_info_items(_rejoin_file_info_strings(nested))
#------------------------------------------------------------------------------#
def get_file_metadata(os_path):
        file_proc = subprocess.Popen(
            ['file', '-b', os_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output, errors = file_proc.communicate()

        return _structure_file_info_string(_tokenize_file_info_string(output))
#------------------------------------------------------------------------------#
def get_file_metadata_date_time(attributes):
    try:
        for attrib in attributes:
            if type(attrib) is list:
                return get_file_metadata_date_time(attrib)
            elif type(attrib) is tuple:
                if type(attrib[1]) is list:
                    return get_file_metadata_date_time(attrib[1])
                elif type(attrib[0]) is str and attrib[0] == 'datetime':
                    if type(attrib[1]) is str:
                        dt_formats = [
                            "%Y-%m-%d %H:%M:%S",
                            "%Y:%m:%d %H:%M:%S"
                        ]
                        for dt_fmt in dt_formats:
                            try: return time.strptime(attrib[1], dt_fmt)
                            except ValueError: pass
    except: pass
#------------------------------------------------------------------------------#
_picture_resolution_reg_ex = re.compile("^(\d+)\s*[Xx]\s*(\d+)$")
#------------------------------------------------------------------------------#
def get_file_metadata_picture_info(attributes):
    width = None
    height = None
    is_picture = False

    for attrib in attributes:
        if type(attrib) is str:
            match = _picture_resolution_reg_ex.match(attrib)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))

    if width and height:
        return (width, height)
#------------------------------------------------------------------------------#

