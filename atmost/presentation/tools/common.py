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
def reduce_by(lst, fact, func = lambda l: float(sum(l))/len(l)):
    t = []
    r = []

    for e in lst:
        t.append(e)
        if len(t) >= fact:
            r.append(func(t))
            t = []

    try: r.append(func(t))
    except: pass
    return r
# ------------------------------------------------------------------------------
