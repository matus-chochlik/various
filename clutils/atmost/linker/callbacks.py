# coding: UTF-8
#  Copyright (c) 2019 Matus Chochlik
import os
import sys
import json
import multiprocessing
# ------------------------------------------------------------------------------
class DriverData(object):
    # --------------------------------------------------------------------------
    def __init__(self):
        pass
# ------------------------------------------------------------------------------
def load_user_data():
    sys.stdout.write("[{}\n")

# ------------------------------------------------------------------------------
def save_user_data(user_data):
    sys.stdout.write("]")

# ------------------------------------------------------------------------------
def is_linker(proc):
    linker_names = [
        'x86_64-linux-gnu-gold',
        'x86_64-linux-gnu-ld',
        'gold',
        'ld'
    ]
    return proc.basename() in linker_names

# ------------------------------------------------------------------------------
def get_ld_info(user_data, proc):
    assert is_linker(proc)
    args = proc.args()[1:]
    cwd = proc.cwd()
    outputs = []
    sinputs = []
    dinputs = []
    plugins = []
    libdirs = []

    prev = None
    for arg in args:
        if prev in ["-L", "--library-path"]:
            if os.path.isdir(arg):
                libdirs.append(arg)
        elif arg.startswith("-L"):
            tmp = arg[len("-L"):].strip()
            if os.path.isdir(tmp):
                libdirs.append(tmp)
        elif arg.startswith("--library-path"):
            tmp = arg[len("--library-path"):].strip()
            if os.path.isdir(tmp):
                libdirs.append(tmp)
        prev = arg

    for arg in ["/usr/local/lib", "/usr/lib", "/lib"]:
        if os.path.isdir(arg):
            libdirs.append(arg)

    libdirs = set([os.path.realpath(p) for p in libdirs])

    def _is_so_path(path):
        temp = path
        while temp:
            temp, ext = os.path.splitext(temp)
            if not ext:
                break
            if ext == ".so":
                return True
        return False

    def _append_lib(name):
        for libdir in libdirs:
            if os.path.isfile(os.path.join(libdir,  "lib%s.so" % name)):
                dinputs.append(os.path.join(libdir, "lib%s.so" % name))
                break
            elif os.path.isfile(os.path.join(libdir, "lib%s.a" % name)):
                sinputs.append(os.path.join(libdir,  "lib%s.a" % name))
                break

    def _append_plgn(path):
        if os.path.isfile(path):
            plugins.append(path)
        elif os.path.isfile(os.path.join(cwd, path)):
            plugins.append(os.path.join(cwd, path))

    opt_level = 0

    prev = None
    for arg in args:
        if arg[0] != '-':
            if prev in ["-O"]:
                try:
                    opt_level = int(arg)
                except TypeError: pass
            else:
                path_arg = None
                if os.path.isfile(arg):
                    path_arg = arg
                elif os.path.isfile(os.path.join(cwd, arg)):
                    path_arg = os.path.join(cwd, arg)

                if path_arg is not None:
                    if prev in ["-o", "--output"]:
                        outputs.append(path_arg)
                    elif prev in ["--plugin", "-plugin"]:
                        plugins.append(path_arg)
                    elif _is_so_path(path_arg):
                        dinputs.append(path_arg)
                    else:
                        sinputs.append(path_arg)
        elif prev in ["-l", "--library"]:
            _append_lib(arg)
        elif arg.startswith("-l"):
            _append_lib(arg[len("-l"):].strip())
        elif arg.startswith("--library"):
            _append_lib(arg[len("--library"):].strip())
        elif arg.startswith("-O"):
            try:
                opt_level = int(arg[len("-O"):])
            except TypeError: pass
        elif arg.startswith("--plugin"):
            _append_plgn(arg[len("--plugin"):].strip())
        elif arg.startswith("-plugin"):
            _append_plgn(arg[len("-plugin"):].strip())

        prev = arg

    sinputs = set([os.path.realpath(p) for p in sinputs])
    dinputs = set([os.path.realpath(p) for p in dinputs])
    plugins = set([os.path.realpath(p) for p in plugins])

    try:
        sco = sum(1 for f in sinputs if os.path.isfile(f))
        dco = sum(1 for f in dinputs if os.path.isfile(f))
        npg = sum(1 for f in plugins if os.path.isfile(f))
        ssz = sum(os.path.getsize(f) for f in sinputs if os.path.isfile(f))
        dsz = sum(os.path.getsize(f) for f in dinputs if os.path.isfile(f))
        osz = sum(os.path.getsize(f) for f in outputs if os.path.isfile(f))
        mem = proc.max_memory_bytes()

        if len(outputs) > 0:
            pie = 1 if ("-pie" in args or "--pic-executable" in args) else 0
            pie = 0 if ("-no-pie" in args or "--no-pic-executable" in args) else pie 
            outpath = os.path.realpath(outputs[0])

            return {
                #"output_path": outpath,
                "plugin_count": npg,
                "static_count": sco,
                "static_size": ssz,
                "shared_count": dco,
                "shared_size": dsz,
                "memory_size": mem,
                "output_size": osz,
                "b_static": 1 if "-Bstatic" in args else 0,
                "b_dynamic": 1 if "-Bdynamic" in args else 0,
                "pie": pie,
                "opt": opt_level
            }
    except: pass

# ------------------------------------------------------------------------------
def let_process_go(user_data, procs):
    proc = procs.current()
    if is_linker(proc):
        if len(procs.active()) < 1:
            return True
        return False
    return len(procs.active()) <  multiprocessing.cpu_count()

# ------------------------------------------------------------------------------
def process_finished(user_data, proc):
    if is_linker(proc):
        info = get_ld_info(user_data, proc)
        if info:
            sys.stdout.write(",")
            json.dump(info, sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()


 
