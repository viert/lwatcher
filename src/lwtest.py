#!/usr/bin/env python

from lwlib.watcher import Watcher
from lwlib.tasks import *

watcher = Watcher('conf/', 'testwatcher.log', 'plugins/')
task = watcher.tasks[0]
worker = watcher.scheduler.pool[0]
worker.performTask(task)
