# coding: UTF-8
#  Copyright (c) 2019 Matus Chochlik
import os
import sys
import math
import json
import gzip
import pickle
import pandas
import multiprocessing
# ------------------------------------------------------------------------------
_1GB = (1024.0**3.0)
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
    if not is_linker(proc):
        return None

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
        pie = 1 if ("-pie" in args or "--pic-executable" in args) else 0
        pie = 0 if ("-no-pie" in args or "--no-pic-executable" in args) else pie 

        return {
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
    except Exception as error:
        sys.stderr.write("atmost: error: %s\n" % error)

# ------------------------------------------------------------------------------
class DriverData(object):
    # --------------------------------------------------------------------------
    def __init__(self, d):
        self._scaler = d["scaler"]
        self._model = d["model"]
        self._fields = d["fields"]
        self._chunk_size = d["chunk_size"]
        self._error_margin = d["error_margin"] * self._chunk_size

    # --------------------------------------------------------------------------
    def estimate_memory_usage(self, proc):
        f = self._fields
        ldi = get_ld_info(self, proc)
        if ldi is not None:
            ldi = {k: float(v) for k, v in ldi.items() if k in f}
            df = pandas.DataFrame(ldi, index=[0])
            cls = self._model.classes_
            pro = self._model.predict_proba(self._scaler.transform(df))
            return sum(p * c for p, c in zip(pro[0], cls)) * self._chunk_size
        return None
    # --------------------------------------------------------------------------
    def error_margin(self):
        return self._error_margin

# ------------------------------------------------------------------------------
def load_user_data():
    sys.stdout.write("[{}\n")
    try:
        return DriverData(pickle.load(gzip.open("atmost.linker.pickle.gz", "rb")))
    except Exception as error:
        sys.stderr.write("atmost: error: %s\n" % error)

# ------------------------------------------------------------------------------
def save_user_data(user_data):
    sys.stdout.write("]")

# ------------------------------------------------------------------------------
def let_process_go(user_data, procs):
    proc = procs.current()
    actp = procs.active()
    actn = len(actp)
    waitn = len(procs.waiting())
    if is_linker(proc):
        # estimated memory usage of the current process
        proc_est_usage = user_data.estimate_memory_usage(proc)
        proc_est_usage += user_data.error_margin()
        # active process memory usage
        active_mem_usage = 0.0

        let_go = False

        if actn > 0:
            total_mem = procs.total_memory()
            avail_mem = procs.available_memory()

            for ap in actp:
                est_usage = ap.callback_data()
                max_usage = ap.max_memory_bytes()
                alpha = math.exp(-ap.run_time() / 120.0)
                active_mem_usage += alpha*est_usage + (1.0-alpha)*max_usage

            if min(total_mem-active_mem_usage, avail_mem) > proc_est_usage:
                let_go = True
        else:
            let_go = True

        if let_go:
            proc.set_callback_data(proc_est_usage)
            sys.stderr.write(
                "atmost: linking: a=%d|w=%d (%4.2f GB / %4.2f GB)\n" % (
                    actn,
                    waitn,
                    active_mem_usage / _1GB,
                    proc_est_usage / _1GB,
                )
            )
            return True
        return False
    return actn <  multiprocessing.cpu_count()

# ------------------------------------------------------------------------------
def process_finished(user_data, proc):
    if is_linker(proc):
        info = get_ld_info(user_data, proc)
        if info:
            sys.stderr.write(
                "atmost: linked: (%4.2f GB / %4.2f GB)\n" % (
                    info["memory_size"] / _1GB,
                    proc.callback_data() / _1GB
                )
            )

            sys.stdout.write(",")
            json.dump(info, sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()

# ------------------------------------------------------------------------------

 
