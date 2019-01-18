# coding=utf-8
# Copyright Matus Chochlik.
# Distributed under the Boost Software License, Version 1.0.
# See accompanying file LICENSE_1_0.txt or copy at
#  http://www.boost.org/LICENSE_1_0.txt
#
import os
import re

class MakeJobServerSlots:
    def __init__(self, rfd, wfd, count):
        self._job_server_read_fd = rfd
        self._job_server_write_fd = wfd
        self._tokens = os.read(rfd, count)

    def __del__(self):
        if self._tokens:
            os.write(self._job_server_write_fd, self._tokens)

    def __nonzero__(self):
        return len(self._tokens)

    def available_slots(self):
        return len(self._tokens)


class MakeJobServerContext:
    def __init__(self):
        self._dry_run = False
        self._has_job_server = False
        self._job_server_read_fd = -1
        self._job_server_write_fd = -1

        for flag in os.environ.get("MAKEFLAGS", "").split():
            if flag == "n":
                self._dry_run = True
            else:
                match = re.match(
                    "--jobserver-(fds|auth)=([0-9]+),([0-9]+)",
                    flag)
                if match:
                    try:
                        rfd = int(match.group(2))
                        wfd = int(match.group(3))
                        self._job_server_read_fd = rfd
                        self._job_server_write_fd = wfd
                        self._has_job_server = True
                    except ValueError:
                        pass

    def dry_run(self):
        return self._dry_run

    def has_job_server(self):
        return self._has_job_server

    def get_slots(self, slot_count):
        return MakeJobServerSlots(
            self._job_server_read_fd,
            self._job_server_write_fd,
            slot_count)

    def get_slot(self):
        return self.get_slots(1)

if __name__ == "__main__":
    ctx = MakeJobServerContext()
    js1 = ctx.get_slot()
    print(js1.available_slots())
