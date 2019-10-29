# ------------------------------------------------------------------------------
import gzip
import json
# ------------------------------------------------------------------------------
class DictObject(object):
    # --------------------------------------------------------------------------
    def __init__(self, src):
        for k, v in src.items():
            self.__dict__[k] = DictObject.make(v)

    # --------------------------------------------------------------------------
    @classmethod
    def make(Class, src):
        if type(src) is dict:
            return Class(src)
        if type(src) is list:
            return [Class.make(e) for e in src]
        if type(src) is tuple:
            return (Class.make(e) for e in src)
        return src
    # --------------------------------------------------------------------------
    @classmethod
    def loadJson(Class, path):
        try:
            return Class.make(json.load(gzip.open(path, "rt")))
        except OSError:
            return Class.make(json.load(open(path, "rt")))
# ------------------------------------------------------------------------------
