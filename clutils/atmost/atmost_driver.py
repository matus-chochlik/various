#!/usr/bin/env python
# coding: UTF-8
#  Copyright (c) 2019 Matus Chochlik

import os
import imp
import time
import json
import string
import errno
import socket
import signal
import psutil
import hashlib
import argparse
import multiprocessing

try:
    import selectors
except ImportError:
    import selectors2 as selectors

# ------------------------------------------------------------------------------
class AtmostCallbacks(object):
    # --------------------------------------------------------------------------
    def __init__(self):
        self.load_user_data = lambda: None
        self.save_user_data = lambda data: None

        self.let_process_go =\
            lambda data, info: len(info.active()) < multiprocessing.cpu_count()
        self.process_finished = lambda data, info: None
# ------------------------------------------------------------------------------
class AtmostDriverArgumentParser(argparse.ArgumentParser):
    # --------------------------------------------------------------------------
    def _try_import_callbacks_py(self, callbacks_path):
        callbacks = AtmostCallbacks()
        try:
            imp.acquire_lock()
            callbacks_py = imp.load_source(
                "atmost",
                os.path.join(callbacks_path)
            )
            try: callbacks.load_user_data = callbacks_py.load_user_data
            except: pass
            try: callbacks.save_user_data = callbacks_py.save_user_data
            except: pass
            try: callbacks.let_process_go = callbacks_py.let_process_go
            except: pass
            try: callbacks.process_finished = callbacks_py.process_finished
            except: pass
        finally:
            imp.release_lock()
        return callbacks

    # --------------------------------------------------------------------------
    def __init__(self, **kw):
        argparse.ArgumentParser.__init__(self, **kw)

        self.add_argument(
            '-s', '--socket',
            metavar='SOCKET-FILE',
            dest='socket_path',
            nargs='?',
            type=os.path.realpath,
            default="/tmp/atmost.socket"
        )

        self.add_argument(
            '-c', '--callbacks',
            metavar='CALLBACK-SCRIPT',
            dest='callbacks_script',
            nargs='?',
            type=os.path.realpath,
            default=None
        )

        self.add_argument(
            '-u', '--update',
            metavar='INTERVAL',
            dest='update_interval',
            nargs='?',
            type=float,
            default=1
        )

    # --------------------------------------------------------------------------
    def process_parsed_options(self, options):
        options.callbacks = AtmostCallbacks()

        if options.callbacks_script is not None:
            path = options.callbacks_script
            if os.path.isfile(path):
                try:
                    options.callbacks = self._try_import_callbacks_py(path)
                except Exception as error:
                    self.error("failed to import callback script '%s': %s" % (
                        path,
                        str(error)
                    ))
            else:
                self.error("'%s' is not a file" % path)
        else:
            path = os.path.realpath("atmost_callbacks.py")
            if os.path.isfile(path):
                try:
                    options.callbacks = self._try_import_callbacks_py(path)
                except: pass
        #
        return options

    # --------------------------------------------------------------------------
    def parse_args(self):
        return self.process_parsed_options(
            argparse.ArgumentParser.parse_args(self)
        )

# ------------------------------------------------------------------------------
def make_argparser():
	return AtmostDriverArgumentParser(
            prog="atmost_driver",
            description="""
            Driver/server for the atmost utility
		"""
	)

# ------------------------------------------------------------------------------
def open_socket(options):
    if options.socket_path:
        try: os.unlink(options.socket_path)
        except OSError as os_error:
            if os_error.errno != errno.ENOENT:
                raise
        uds = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        uds.bind(options.socket_path)
        uds.listen(100)
        uds.setblocking(False)
        return uds

# ------------------------------------------------------------------------------
class AtmostProcess(object):
    # --------------------------------------------------------------------------
    def __init__(self, uid, parent):
        self._uid = uid
        self._parent = parent
        self._input_buff = str()
        self._output_buff = str()
        self._json = None
        self._pid = -1
        self._arguid = None
        self._psutil = None
        self._responded = False
        self._create_time = time.time()
        self._ready_time = None
        self._let_go_time = None
        self._max_mem_usage = -1
        self._digest_trans = string.maketrans('0123456789', 'ghijklmnop')

    # --------------------------------------------------------------------------
    def __add__(self, other):
        if type(other) == AtmostProcess:
            return AtmostProcessList([self, other])
        if type(other) == AtmostProcessList:
            return AtmostProcessList([self] + list(other))
        raise TypeError

    # --------------------------------------------------------------------------
    def __eq__(self, other):
        return self._pid != -1 and other._pid != -1 and self._pid == other._pid

    # --------------------------------------------------------------------------
    def __ne__(self, other):
        return not self == other

    # --------------------------------------------------------------------------
    def update(self):
        try:
            self._max_mem_usage = max(
                self._max_mem_usage,
                self._psutil.memory_info().rss
            )
        except: pass

    # --------------------------------------------------------------------------
    def life_time(self):
        return time.time() - self._create_time

    # --------------------------------------------------------------------------
    def wait_time(self):
        if self._ready_time is not None:
            if self._let_go_time is not None:
                return self._let_go_time - self._ready_time
            else:
                return time.time() - self._ready_time
        return 0.0

    # --------------------------------------------------------------------------
    def run_time(self):
        if self._let_go_time is not None:
            return time.time() - self._let_go_time
        return 0.0

    # --------------------------------------------------------------------------
    def got_response(self):
        return self._responded

    # --------------------------------------------------------------------------
    def command_uid(self):
        return self._arguid

    # --------------------------------------------------------------------------
    def args(self):
        try: return self._json["args"]
        except: return []

    # --------------------------------------------------------------------------
    def exe(self):
        try: return self._json["args"][0]
        except: pass

    # --------------------------------------------------------------------------
    def basename(self):
        try: return os.path.basename(self._json["args"][0])
        except: pass

    # --------------------------------------------------------------------------
    def environment(self):
        try: return self._psutil.environ()
        except: pass

    # --------------------------------------------------------------------------
    def cwd(self):
        try: return self._psutil.cwd()
        except: pass

    # --------------------------------------------------------------------------
    def username(self):
        try: return self._psutil.username()
        except: pass

    # --------------------------------------------------------------------------
    def usernames(self):
        try: return [self._psutil.username()]
        except: []

    # --------------------------------------------------------------------------
    def status(self):
        try: return self._psutil.status()
        except: pass

    # --------------------------------------------------------------------------
    def num_threads(self):
        try: return self._psutil.num_threads()
        except: return 0

    # --------------------------------------------------------------------------
    def cpu_percent(self, interval=1):
        try: return self._psutil.cpu_percent(interval)
        except: return 0

    # --------------------------------------------------------------------------
    def memory_percent(self):
        try: return self._psutil.memory_percent()
        except: return 0

    # --------------------------------------------------------------------------
    def max_memory_bytes(self):
        return self._max_mem_usage

    # --------------------------------------------------------------------------
    def is_ready(self):
        return self._pid is not None and self._pid > 0

    # --------------------------------------------------------------------------
    def is_running(self):
        if self._pid > 0:
            try:
                os.kill(self._pid, 0)
                return True
            except OSError:
                pass
        return False

    # --------------------------------------------------------------------------
    def go(self, conn):
        self.update()
        self._responded = True
        self._let_go_time = time.time()
        self._output_buff = "OK-GO\n"
        self.handle_write(conn)

    # --------------------------------------------------------------------------
    def disconnect(self, conn):
        self._parent.disconnect_client(self._uid, conn)

    # --------------------------------------------------------------------------
    def command_line_uid(self):
        h = hashlib.sha1()
        for arg in self.args():
            h.update(arg)
        return h.hexdigest().translate(self._digest_trans)

    # --------------------------------------------------------------------------
    def handle_read(self, conn):
        try:
            data = conn.recv(1024)
            if data:
                self._input_buff += str(data)
                try:
                    self._json = json.loads(self._input_buff)
                    self._pid = int(self._json["pid"])
                    self._arguid = self.command_line_uid()
                    self._psutil = psutil.Process(self._pid)
                    self._ready_time = time.time()
                except:
                    pass
            else:
                self.disconnect(conn)
        except socket.error:
                self.disconnect(conn)

    # --------------------------------------------------------------------------
    def handle_write(self, conn):
        if self._output_buff:
            done = conn.send(self._output_buff)
            self._output_buff = self._output_buff[done:]
            if not self._output_buff:
                self.disconnect(conn)

# ------------------------------------------------------------------------------
class AtmostProcessList(list):
    # --------------------------------------------------------------------------
    def __init__(self, items):
        list.__init__(self)
        self.extend(items)

    # --------------------------------------------------------------------------
    def __add__(self, other):
        if type(other) == AtmostProcessList:
            return AtmostProcessList(list(self) + list(other))
        if type(other) == AtmostProcess:
            return AtmostProcessList(list(self) + [other])
        raise TypeError

    # --------------------------------------------------------------------------
    def __len__(self):
        return list.__len__(self)

    # --------------------------------------------------------------------------
    def __iter__(self):
        return list.__iter__(self)

    # --------------------------------------------------------------------------
    def __getitem__(self, key):
        return list.__getitem__(self, key)

    # --------------------------------------------------------------------------
    def __delitem__(self, key):
        return list.__delitem__(self, key)

    # --------------------------------------------------------------------------
    def usernames(self):
        return list(set(n for p in self for n in p.usernames()))

    # --------------------------------------------------------------------------
    def num_threads(self):
        return sum([p.num_threads() for p in self])

    # --------------------------------------------------------------------------
    def cpu_percent(self, interval=1):
        return sum([p.cpu_percent(interval) for p in self])

    # --------------------------------------------------------------------------
    def memory_percent(self):
        return sum([p.memory_percent() for p in self])

    # --------------------------------------------------------------------------
    def max_memory_bytes(self):
        return sum([p.max_memory_bytes() for p in self])

# ------------------------------------------------------------------------------
class AtmostFilterContext(object):
    # --------------------------------------------------------------------------
    def __init__(self, clients, current):
        self._clients = clients
        self._current = current

    # --------------------------------------------------------------------------
    def total_memory(self):
        return psutil.virtual_memory().total

    # --------------------------------------------------------------------------
    def available_memory(self):
        return psutil.virtual_memory().available

    # --------------------------------------------------------------------------
    def current(self):
        return self._current

    # --------------------------------------------------------------------------
    def active(self):
        def _filter(x):
            return x.got_response() and x.is_running() and x != self._current
        return AtmostProcessList([x for x in self._clients if _filter(x)])

    # --------------------------------------------------------------------------
    def waiting(self):
        def _filter(x):
            return not x.got_response() and x.is_running() and x != self._current
        return AtmostProcessList([x for x in self._clients if _filter(x)])

# ------------------------------------------------------------------------------
class AtmostDriver(object):
    # --------------------------------------------------------------------------
    def __init__(self, selector, callbacks, user_data):
        self._selector = selector
        self._callbacks = callbacks
        self._user_data = user_data
        self._clients = dict()

    # --------------------------------------------------------------------------
    def add_client(self, client_id, conn, client):
        self._clients[client_id] = (conn, client)
        self._selector.register(
            conn,
            selectors.EVENT_READ|
            selectors.EVENT_WRITE,
            data = client
        )

    # --------------------------------------------------------------------------
    def disconnect_client(self, client_id, conn):
        self._selector.unregister(conn)
        conn.close()
        del conn

    # --------------------------------------------------------------------------
    def remove_client(self, client_id, conn):
        self._callbacks.process_finished(
            self._user_data,
            self._clients[client_id][1])
        del conn
        del self._clients[client_id]

    # --------------------------------------------------------------------------
    def cleanup(self):
        to_be_removed = []
        for uid, (conn, client) in self._clients.items():
            if client.is_ready() and not client.is_running():
                to_be_removed.append((uid, conn))

        for uid, conn in to_be_removed:
            self.remove_client(uid, conn)

    # --------------------------------------------------------------------------
    def let_go(self, info):
        return self._callbacks.let_process_go(self._user_data, info)

    # --------------------------------------------------------------------------
    def respond(self):
        clients = [client for conn, client in self._clients.values()]
        for (conn, curr) in self._clients.values():
            if curr.is_ready() and not curr.got_response():
                if self.let_go(AtmostFilterContext(clients, curr)):
                    curr.go(conn)

    # --------------------------------------------------------------------------
    def update(self):
        for conn, client in self._clients.values():
            client.update()
        self.cleanup()
        self.respond()

# ------------------------------------------------------------------------------
keep_running = True
# ------------------------------------------------------------------------------
def drive_atmost(options):
    user_data = None
    try: user_data = options.callbacks.load_user_data()
    except: pass

    try:
        global keep_running
        lsock = open_socket(options)
        with selectors.DefaultSelector() as selector:
            driver = AtmostDriver(selector, options.callbacks, user_data)
            selector.register(
                lsock,
                selectors.EVENT_READ,
                data = driver
            )

            client_id  = 0
            while keep_running:
                events = selector.select(timeout=options.update_interval)
                for key, mask in events:
                    if type(key.data) is AtmostDriver:
                        state = key.data
                        conn, addr = lsock.accept()
                        conn.setblocking(False)
                        client = AtmostProcess(client_id, state)
                        state.add_client(client_id, conn, client)
                        client_id += 1
                    elif type(key.data) is AtmostProcess:
                        client = key.data
                        conn = key.fileobj
                        if mask & selectors.EVENT_READ:
                            client.handle_read(conn)
                        if mask & selectors.EVENT_WRITE:
                            client.handle_write(conn)
                driver.update()
    finally:
        try: lsock.close()  
        except: pass

    try: options.callbacks.save_user_data(user_data)
    except: pass

# ------------------------------------------------------------------------------
def handle_interrupt(sig, frame):
    global keep_running
    keep_running = False
# ------------------------------------------------------------------------------
def main():
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)
    drive_atmost(make_argparser().parse_args())
    return 0
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    exit(main())
# ------------------------------------------------------------------------------
