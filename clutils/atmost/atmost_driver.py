#!/usr/bin/env python
# coding: UTF-8
#  Copyright (c) 2019 Matus Chochlik

import os
import imp
import json
import errno
import socket
import signal
import argparse
import multiprocessing

try:
    import selectors
except ImportError:
    import selectors2 as selectors

# ------------------------------------------------------------------------------
class AtmostDriverArgumentParser(argparse.ArgumentParser):
    # --------------------------------------------------------------------------
    def _try_import_filter_py(self, filter_path):
        try:
            imp.acquire_lock()
            filter_py = imp.load_source(
                "atmost",
                os.path.join(filter_path)
            )
            return filter_py.release_process
        except:
            imp.release_lock()
            raise
        finally:
            imp.release_lock()

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
            '-f', '--filter',
            metavar='FILTER-SCRIPT',
            dest='filter_script',
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
        options.filter_func =\
                lambda info: len(info.active()) < multiprocessing.cpu_count()

        if options.filter_script is not None:
            path = options.filter_script
            if os.path.isfile(path):
                try:
                    options.filter_func = self._try_import_filter_py(path)
                except Exception as error:
                    self.error("failed to import filter script '%s': %s" % (
                        path,
                        str(error)
                    ))
            else:
                self.error("'%s' is not a file" % path)
        else:
            path = os.path.realpath("atmost_filter.py")
            if os.path.isfile(path):
                try:
                    options.filter_func = self._try_import_filter_py(path)
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
        self._responded = False

    # --------------------------------------------------------------------------
    def __eq__(self, other):
        return self._pid != -1 and other._pid != -1 and self._pid == other._pid

    # --------------------------------------------------------------------------
    def __ne__(self, other):
        return not self == other

    # --------------------------------------------------------------------------
    def got_response(self):
        return self._responded

    # --------------------------------------------------------------------------
    def args(self):
        try:
            return self._json["args"]
        except:
            return []

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
        self._responded = True
        self._output_buff = "OK-GO\n"
        self.handle_write(conn)

    # --------------------------------------------------------------------------
    def disconnect(self, conn):
        self._parent.disconnect_client(self._uid, conn)

    # --------------------------------------------------------------------------
    def handle_read(self, conn):
        try:
            data = conn.recv(1024)
            if data:
                self._input_buff += str(data)
                try:
                    self._json = json.loads(self._input_buff)
                    self._pid = int(self._json["pid"])
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
class AtmostProcesses(object):
    # --------------------------------------------------------------------------
    def __init__(self, clients, current):
        self._clients = clients
        self._current = current

    # --------------------------------------------------------------------------
    def current(self):
        return self._current

    # --------------------------------------------------------------------------
    def active(self):
        def _filter(x):
            return x.got_response() and x.is_running() and x != self._current
        return [x for x in self._clients if _filter(x)]

    # --------------------------------------------------------------------------
    def waiting(self):
        def _filter(x):
            return not x.got_response() and x.is_running() and x != self._current
        return [x for x in self._clients if _filter(x)]

# ------------------------------------------------------------------------------
class AtmostDriver(object):
    # --------------------------------------------------------------------------
    def __init__(self, selector, release_filter):
        self._selector = selector
        self._release_process = release_filter
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
        return self._release_process(info)

    # --------------------------------------------------------------------------
    def respond(self):
        clients = [client for conn, client in self._clients.values()]
        for (conn, curr) in self._clients.values():
            if curr.is_ready() and not curr.got_response():
                if self.let_go(AtmostProcesses(clients, curr)):
                    curr.go(conn)

    # --------------------------------------------------------------------------
    def update(self):
        self.cleanup()
        self.respond()

# ------------------------------------------------------------------------------
keep_running = True
# ------------------------------------------------------------------------------
def drive_atmost(options):
    try:
        global keep_running
        lsock = open_socket(options)
        with selectors.DefaultSelector() as selector:
            driver = AtmostDriver(selector, options.filter_func)
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
