#!/usr/bin/env python3
# coding=utf8

import sys
import re
import json
import gzip

re_filename = re.compile(".*[.-][Jj]?([0-9]+)[Jj]?\.json.gz")
re_arrived = re.compile("^atmost: arrived '(.+)'")
re_linking = re.compile("^atmost: linking '(.+)': \(predicted=([0-9.-]+)G±([0-9.-]+)G\|available=([0-9.-]+)G\)")
re_linked  = re.compile("^atmost: linked  '(.+)': \(predicted=([0-9.-]+)G±([0-9.-]+)G\|actual=([0-9.-]+)G\)")

try:
    data = []
    for arg in sys.argv[1:]:
        match = re_filename.search(arg)
        if match:
            jobs = int(match.group(1))
            jk = "j%d" % jobs
            targets = {}
            with gzip.open(arg, "rt") as inp:
                jd = json.load(inp)
                for attr in jd:
                    line = attr["line"]
                    del attr["line"]
                    match = re_arrived.search(line)
                    if match:
                        targets[match.group(1)] = {
                            "name": match.group(1),
                            "arrived": attr}
                    else:
                        match = re_linking.search(line)
                        if match:
                            attr["predicted"] = float(match.group(2))
                            attr["error"] = float(match.group(3))
                            attr["available"] = float(match.group(4))
                            targets[match.group(1)]["linking"] = attr
                        else:
                            match = re_linked.search(line)
                            if match:
                                attr["predicted"] = float(match.group(2))
                                attr["error"] = float(match.group(3))
                                attr["actual"] = float(match.group(4))
                                targets[match.group(1)]["linked"] = attr
                            else:
                                sys.stderr.write(line)
            data.append({"jobs": jobs, "targets": [x for x in targets.values()]})
    json.dump(data, sys.stdout)
except BrokenPipeError:
    pass
except KeyboardInterrupt:
    pass
