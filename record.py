#!/usr/bin/env python
from __future__ import division, print_function

import re
import os
import sys
import time
import datetime
import subprocess

BASE_DIR = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))


class Window(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs


def main():

    wids = {}
    temp = os.popen('./GetWindowList 2>&1').read().strip().split('},')
    for i in temp:
        name = re.search(r'kCGWindowName = "([^"]+)";', i)
        name = name and name.group(1)
        pid = re.search(r'kCGWindowOwnerPID = (\d+);', i)
        pid = pid and pid.group(1)
        owner = re.search(r'kCGWindowOwnerName = "([^"]+)";', i)
        owner = owner and owner.group(1)
        wid = re.search(r'kCGWindowNumber = (\d+);', i)
        wid = wid and wid.group(1)
        if pid and name and owner and wid:
            wids[str(wid)] = Window(
                pid=pid,
                name=name,
                owner=owner,
                wid=wid,
            )
    try:
        w = wids[sys.argv[1]]
    except (IndexError, KeyError):
        for w in sorted(wids.values(), key=lambda w: (w.name, w.wid)):
            print("%8s: %s (pid:%s) -> %s" % (w.wid, w.owner, w.pid, w.name), file=sys.stderr)
        return 64

    print("Starting Recording", file=sys.stderr)
    print("==================", file=sys.stderr)
    print("Recording window %s: %s (pid:%s) -> %s" % (w.wid, w.owner, w.pid, w.name), file=sys.stderr)

    seconds = 10
    for wait in range(5, 0, -1):
        print("For %s seconds, starting in %s seconds..." % (seconds, wait), end="\r", file=sys.stderr)
        time.sleep(1)
    print("\033[2K\rRecording for %s seconds..." % seconds, file=sys.stderr)

    now = datetime.datetime.now()
    stop = now + datetime.timedelta(seconds=seconds)

    while now < stop:
        filename = "capture/screen_%s.png" % int(time.time() * 1000)
        # print("Saving screen: %s" % filename, file=sys.stderr)
        print(".", end="", file=sys.stderr)
        cmd = ["screencapture", "-o", "-x", "-C", "-l%s" % w.wid, os.path.join(BASE_DIR, filename)]
        subprocess.call(cmd)

        time.sleep(1 / 60)
        now = datetime.datetime.now()

    time.sleep(1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
