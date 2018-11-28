#!/usr/bin/env python
# coding=utf-8
# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt
#
#
from __future__ import print_function
import os
import sys
import stat
import signal
import argparse
import subprocess
import tempfile
import json
import time
import re

# ------------------------------------------------------------------------------
class ArgumentParser(argparse.ArgumentParser):

    # -------------------------------------------------------------------------
    def stable_config_path(self, arg):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            "share",
            "proman",
            "config",
            arg
        )

    # -------------------------------------------------------------------------
    def site_config_path(self, arg):
        return os.path.join("/etc/proman", arg)

    # -------------------------------------------------------------------------
    def user_config_path(self, arg):
        return os.path.join(
            os.path.expanduser("~"),
            ".config",
            "proman",
            arg)

    # -------------------------------------------------------------------------
    def config_search_paths(self, arg):
        return [
            os.path.abspath(arg),
            self.stable_config_path(arg),
            self.site_config_path(arg),
            self.user_config_path(arg)
        ]

    # -------------------------------------------------------------------------
    def config_search_exts(self):
        return [".procfg", ".json", ""]

    # -------------------------------------------------------------------------
    def find_config_path(self, arg):
        for path in self.config_search_paths(arg):
            for ext in self.config_search_exts():
                tmp = path + ext
                if os.path.isfile(tmp):
                    return tmp

    # -------------------------------------------------------------------------
    def find_config_names(self, arg):
        result = []
        for path in self.config_search_paths(arg):
            for ext in self.config_search_exts():
                if os.path.isfile(path + ext):
                    result.append(os.path.basename(path))
        return result

    # -------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        def config_path(arg):
            result = self.find_config_path(arg)
            return result if result else arg

        self.add_argument(
            dest="config_paths",
            metavar="config",
            type=config_path,
            nargs='*',
            help="""
                Specifies the path to or the name of a configuration file.
                Configuration files are read in the order specified on
                the command line. Variables in later files replace variables
                from earlier files. If config is not a valid filesystem path,
                then following paths `%(paths)s', are searched for files with
                names specified in config, with extensions: `%(exts)s'.
                Currently visible configs: `%(configs)s'.
            """ % {
                "paths": "', `".join(self.config_search_paths("config")),
                "exts": "', `".join(self.config_search_exts()),
                "configs": "', `".join(self.find_config_names('config'))
            }
        )

        def key_value(arg):
            sep = '='
            tmp = arg.split(sep)
            return (tmp[0], sep.join(tmp[1:]))

        self.add_argument(
            "--set",
            dest="overrides",
            metavar="variable=value",
            type=key_value,
            action="append",
            default=[],
            help="""
                Specifies new values for the config variables.
                Variables from loaded configuration files are always overriden,
                by values specified on the command-line.
            """
        )

        self.add_argument(
            "--print-config",
            action="store_true",
            default=False,
            help="""Prints the fully loaded and merged process configuration."""
        )

        self.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="""Does not actually start anything just prints selected information."""
        )

    # -------------------------------------------------------------------------
    def process_parsed_options(self, options):
        for config_path in options.config_paths:
            if not os.path.isfile(config_path):
                self.error("'%s' is not a config file name or path" % (config_path))

        return options

    # -------------------------------------------------------------------------
    def parse_args(self):
        return self.process_parsed_options(
            argparse.ArgumentParser.parse_args(self)
        )

# ------------------------------------------------------------------------------
def get_argument_parser():
    return ArgumentParser(
        prog=os.path.basename(__file__),
        description="""launches and manages a group of processes"""
    )

# ------------------------------------------------------------------------------
def merge_configs(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_configs(value, node)
        elif isinstance(value, list):
            node = destination.setdefault(key, [])
            node += value
        else:
            destination[key] = value

    return destination

# ------------------------------------------------------------------------------
class ProcessConfig(object):

    # -------------------------------------------------------------------------
    def _fallback(self, name):
        if name in ["SELF"]:
            return os.path.abspath(__file__)

        if name in ["BINDIR", "BINARY_DIR"]:
            return os.path.dirname(__file__)

        if name in ["TMPDIR", "TEMPDIR"]:
            return tempfile.gettempdir()

        if name in ["HOME"]:
            return os.path.expanduser("~")

        if name in ["LOGDIR"]:
            return "/var/log"

        if name in ["DATADIR"]:
            return "/var/run"

        if name in ["EXEPATH"]:
            return "$(which ${EXENAME})"

        if name in ["EXEID"]:
            return "$(pathid ${EXEPATH})"

        if name in ["LOGPATH"]:
            return "${LOGDIR}/${EXENAME}.log"

        if name in ["LOG_SEVERITY"]:
            return "info"

        return name

    # -------------------------------------------------------------------------
    def _resolve_cmd_which(self, name):
        search_dirs = os.environ.get("PATH", "").split(':')
        search_dirs += os.path.dirname(__file__)
        for dir_path in search_dirs:
            cmd_path = os.path.join(dir_path, name)
            if os.path.isfile(cmd_path):
                if stat.S_IXUSR & os.stat(cmd_path)[stat.ST_MODE]:
                    return cmd_path
        return name

    # -------------------------------------------------------------------------
    def _resolve_cmd_pathid(self, name):
        return int(hash(name))

    # -------------------------------------------------------------------------
    def _do_resolve_env_vars(self, cmd_res, var_re, eval_re, name, variables):
        value = str(variables.get(name, os.environ.get(name, self._fallback(name))))

        while True:
            found = re.match(var_re, value)
            if found:
                prev = value[:found.start(1)]
                repl = self._do_resolve_env_vars(
                    cmd_res,
                    var_re,
                    eval_re,
                    found.group(2),
                    variables)
                folw = value[found.end(1):]
                value = prev+repl+folw
            else: break

        while True:
            found = re.match(eval_re, value)
            if found:
                prev = value[:found.start(1)]
                repl = str(eval(found.group(2)))
                folw = value[found.end(1):]
                value = prev+repl+folw
            else: break

        while True:
            found_cmd = None
            for cmd_name, cmd_re_func in cmd_res.items():
                cmd_re, cmd_func = cmd_re_func
                found = re.match(cmd_re, value)
                if found:
                    found_cmd = cmd_name
                    break

            if found_cmd:
                prev = value[:found.start(1)]
                repl = str(cmd_func(found))
                folw = value[found.end(1):]
                value = prev+repl+folw
            else: break

        return value

    # -------------------------------------------------------------------------
    def _resolve_env_vars(self, cmd_res, var_re, list_re, eval_re, names, variables, info):
        tmp_env = variables.copy()
        tmp_env.update(info.get("variables", {}))
        if type(names) is not list:
            names = [names]

        for name in names:
            value = self._do_resolve_env_vars(
                cmd_res,
                var_re,
                eval_re,
                name,
                tmp_env)

            found = re.match(list_re, value)
            if found:
                prev = value[:found.start(1)]
                repl = variables.get(found.group(2), [])
                folw = value[found.end(1):]
                if type(repl) is not list:
                    repl = [repl]

                for nested_value in self._resolve_env_vars(
                    cmd_res,
                    var_re,
                    list_re,
                    eval_re,
                    [prev+name+folw for name in repl],
                    tmp_env,
                    info): yield nested_value
            else:
                yield value

    # -------------------------------------------------------------------------
    def __init__(self, options):
        self.full_config = {}

        if options.config_paths:
            for config_path in options.config_paths:
                try:
                    with open(config_path) as config_file:
                        partial_config = json.load(config_file)
                        self.full_config = merge_configs(
                            partial_config,
                            self.full_config)
                except IOError as io_error:
                    print("error reading '%s': %s" % (config_path, io_error))
                except ValueError as value_error:
                    print("error parsing '%s': %s" % (config_path, value_error))

        for key, value in options.overrides:
            self.full_config["variables"][key] = value

        cmd_res = {
            "which": (
                re.compile(".*(\$\(which (\w*)\)).*"),
                lambda match : self._resolve_cmd_which(match.group(2))
            ),
            "pathid": (
                re.compile(".*(\$\(pathid (([/]\w*)*)\)).*"),
                lambda match : self._resolve_cmd_pathid(match.group(2))
            )
        }

        var_re = re.compile(".*(\${([A-Za-z][A-Za-z_0-9]*)}).*")
        list_re = re.compile(".*(\$\[([A-Za-z][A-Za-z_0-9]*)\.\.\.\]).*")
        eval_re = re.compile(".*(\$\(([0-9+*/%-]*)\)).*")
        env = self.full_config.get("variables", {})
        resolve = lambda args, info : self._resolve_env_vars(
            cmd_res,
            var_re,
            list_re,
            eval_re,
            args,
            env,
            info
        )

        for info in self.full_config.get("processes", []):
            info["cmd"] = [x for x in resolve(info["args"], info)]

        if options.print_config:
            print(
                json.dumps(
                    self.full_config,
                    sort_keys=True,
                    indent=2,
                    separators=(', ', ': ')
                )
            )

    def process_infos(self):
        return self.full_config.get("processes", [])

# ------------------------------------------------------------------------------
class ProcessInfo(object):

    # -------------------------------------------------------------------------
    def __init__(self, info):
        self.start_attempts = 0
        self.pid = -1
        self.info = info
        self.handle = None
        self.start_time = None
        self.stop_time = None

    # -------------------------------------------------------------------------
    def __del__(self):
        try:
            self.terminate()
        except:
            pass

    # -------------------------------------------------------------------------
    def close_on_terminate(self):
        return bool(self.info.get("autoclose", False))

    # -------------------------------------------------------------------------
    def is_running(self):
        return self.handle

    # -------------------------------------------------------------------------
    def reset(self):
        self.pid = -1
        self.start_time = None
        self.handle = None

    # -------------------------------------------------------------------------
    def start(self):
        max_restarts = 3
        try: max_restarts = self.info.get["max_restarts"]
        except: pass

        if self.start_attempts < max_restarts:
            print("starting process '%(name)s': %(cmd)s" % self.info)
            self.start_attempts += 1
            try:
                self.handle = subprocess.Popen(self.info["cmd"])
                self.pid = self.handle.pid
                self.info["pid"] = self.pid
                self.start_time = time.clock()
                print("started process '%(name)s' (%(pid)d)" % self.info)
                return True
            except:
                print("failed to start process '%(name)s'" % self.info)
        else:
            print("maximum number of restarts for '%(name)s' reached" % self.info)

        return False

    # -------------------------------------------------------------------------
    def terminate(self):
        if self.handle:
            print("terminating process %(name)s (%(pid)d)" % self.info)
            self.handle.terminate()
            self.reset()
            self.stop_time = time.clock()

# ------------------------------------------------------------------------------
class ProcessList(object):

    # -------------------------------------------------------------------------
    def __init__(self, process_config):
        self.infos = {
            info["name"]:
                ProcessInfo(info) for info in process_config.process_infos()
        }
        self.terminating = False
        self.done = False

    # -------------------------------------------------------------------------
    def manage(self):

        all_running = False
        while not all_running:
            all_running = True
            for name, process in self.infos.items():
                if not process.is_running():
                    can_start = True
                    for dep in process.info.get("depends", []):
                        dep_proc = self.infos.get(dep.get("name"))
                        if dep_proc:
                            dep_delay = float(dep.get("delay", 0))
                            if dep_proc.start_time is None:
                                can_start = False
                            elif dep_proc.start_time + dep_delay > time.clock():
                                can_start = False

                    if can_start:
                        if not process.start():
                            return False
                    else:
                        all_running = False
        return True

    # -------------------------------------------------------------------------
    def restart(self, pid):
        for name, process in self.infos.items():
            if process.pid == pid:
                process.reset()
                if not process.close_on_terminate():
                    if self.manage():
                        return True

        return False

    # -------------------------------------------------------------------------
    def terminate(self):

        self.terminating = True
        for name, process in self.infos.items():
            if process.is_running():
                process.terminate()
        self.done = True

# ------------------------------------------------------------------------------
processes = None
# ------------------------------------------------------------------------------
def terminate_handler(signum, frame):
    global processes
    processes = None

# ------------------------------------------------------------------------------
def child_handler(signum, frame):
    global processes

    try:
        pid, signum = os.waitpid(-1, os.WNOHANG)
        if processes:
            if not processes.restart(pid):
                processes = None
    except OSError:
        pass

# ------------------------------------------------------------------------------
def main():
    argparser = get_argument_parser()
    options = argparser.parse_args()
    config = ProcessConfig(options)

    global processes
    processes = ProcessList(config)

    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    signal.signal(signal.SIGCHLD, child_handler)

    if not options.dry_run:
        if processes.manage():
            while processes:
                signal.pause()

# ------------------------------------------------------------------------------
if __name__ == "__main__": main()
