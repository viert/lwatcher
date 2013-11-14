#!/usr/bin/env python

from lwlib import Watcher
from pprint import pprint

w = Watcher("./conf", "testwatcher.log")
pprint(w.tasks)
