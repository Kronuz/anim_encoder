#!/usr/bin/env python
from __future__ import division, print_function

import re
import os
import sys
import time
import subprocess

BASE_DIR = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
FRAME_DELAY = 1 / 24


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

    usage = False

    try:
        output = sys.argv[1]
    except (IndexError, KeyError):
        usage = True

    try:
        w = wids[sys.argv[2]]
    except (IndexError, KeyError):
        usage = True

    try:
        seconds = int(sys.argv[3])
    except IndexError:
        seconds = 10
    except:
        usage = True

    if usage:
        print("usage: %s <output> <windowid> [seconds]" % sys.argv[0], file=sys.stderr)
        print("  windowid   window ID (see below)", file=sys.stderr)
        print("  seconds    recording time", file=sys.stderr)
        print("", file=sys.stderr)
        print("Current windows:", file=sys.stderr)
        for w in sorted(wids.values(), key=lambda w: (w.name, w.wid)):
            print("%8s: %s (pid:%s) -> %s" % (w.wid, w.owner, w.pid, w.name), file=sys.stderr)
        return 64

    print("Starting Recording", file=sys.stderr)
    print("==================", file=sys.stderr)
    print("Recording window %s: %s (pid:%s) -> %s" % (w.wid, w.owner, w.pid, w.name), file=sys.stderr)

    dirname = os.path.normpath(os.path.join(BASE_DIR, output))
    try:
        os.makedirs(dirname)
    except OSError:
        pass

    for wait in range(5, 0, -1):
        print("For %s seconds, starting in %s seconds..." % (seconds, wait), end="\r", file=sys.stderr)
        time.sleep(1)
    print("\033[2K\rRecording for %s seconds...\a" % seconds, file=sys.stderr)

    start = time.time()
    stop = start + seconds

    processes = []
    while start < stop:
        print(".", end="", file=sys.stderr)
        filename = "screen_%s.png" % int(start * 1000)
        cmd = [
            'screencapture',
            '-r',             # do not add dpi meta data to image
            '-o',             # in window capture mode, do not capture the shadow of the window
            '-x',             # do not play sounds
            '-C',             # capture the cursor as well as the screen. only in non-interactive modes
            '-l%s' % w.wid,   # capture this windowsid
            os.path.join(dirname, filename),
        ]
        process = subprocess.Popen(cmd)
        processes.append(process)
        end = time.time()

        sleep = FRAME_DELAY - (end - start)
        if sleep > 0:
            time.sleep(sleep)
            start = time.time()
        else:
            start = end

    print("\a", file=sys.stderr)

    for process in processes:
        process.wait()

    return 0


if __name__ == '__main__':
    sys.exit(main())
