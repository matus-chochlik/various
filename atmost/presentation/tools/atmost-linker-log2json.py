#!/usr/bin/env python3
# coding=utf8

import sys
import re
import json
import gzip

re_filename = re.compile(".*\.([0-9]+)\.txt.*")
re_arrived = re.compile("^({.*})\|atmost: arrived '(.+)'")
re_linking = re.compile("^({.*})\|atmost: linking '(.+)': \(predicted=([0-9.-]+)G±([0-9.-]+)G\|available=([0-9.-]+)G\)")
re_linked  = re.compile("^({.*})\|atmost: linked  '(.+)': \(predicted=([0-9.-]+)G±([0-9.-]+)G\|actual=([0-9.-]+)G\)")

try:
    data = []
    for arg in sys.argv:
        match = re_filename.search(arg)
        if match:
            jobs = int(match.group(1))
            jk = "j%d" % jobs
            targets = {}
            with gzip.open(arg, "rt") as inp:
                while True:
                    line = inp.readline()
                    if not(line): break
                    attr = {}
                    match = re_arrived.search(line)
                    if match:
                        attr = json.loads(match.group(1))
                        targets[match.group(2)] = {
                            "name": match.group(2),
                            "arrived": attr}
                    else:
                        match = re_linking.search(line)
                        if match:
                            attr = json.loads(match.group(1))
                            attr["predicted"] = float(match.group(3))
                            attr["error"] = float(match.group(4))
                            attr["available"] = float(match.group(5))
                            targets[match.group(2)]["linking"] = attr
                        else:
                            match = re_linked.search(line)
                            if match:
                                attr = json.loads(match.group(1))
                                attr["predicted"] = float(match.group(3))
                                attr["error"] = float(match.group(4))
                                attr["actual"] = float(match.group(5))
                                targets[match.group(2)]["linked"] = attr
                            else:
                                sys.stderr.write(line)
            data.append({"jobs": jobs, "targets": [x for x in targets.values()]})
    json.dump(data, sys.stdout)
except BrokenPipeError:
    pass
except KeyboardInterrupt:
    pass
