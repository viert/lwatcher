#!/usr/bin/env python

import random, time, threading, Queue
import logging
from store import Store

class Task(object):
  def __init__(self, collector_name, log, parser, variables, period, dispersion, index_fields):
    self.collector_name = collector_name
    self.parser = parser
    self.log = log
    self.variables = variables
    self.period = period
    self.dispersion = dispersion
    self.index_fields = index_fields
    self.doneAt = time.time()
    self.setNextStart()
    self.processing = False
    
  def setNextStart(self):
    if self.doneAt is None:
      # first time start in min dispersion seconds
      self.nextStart = time.time() + random.randint(0, self.dispersion)
    else:
      deviation = random.randint(-self.dispersion, self.dispersion)
      self.nextStart = self.doneAt + self.period + deviation

  def setQueued(self):
    self.processing = True
    return self
  
  def setDone(self):
    self.doneAt = time.time()
    self.processing = False
    self.setNextStart()
    return 
  
  def __repr__(self):
    return "<Task collector_name=%s log=%s processing=%s doneAt=%.2f nextStart=%.2f>" % (self.collector_name, self.log, self.processing, self.doneAt, self.nextStart)
  
  
  def isReady(self):
    return not self.processing and (time.time() >= self.nextStart)

class StoppableThread(threading.Thread):
  def __init__(self):
    self._stopped = False
    threading.Thread.__init__(self)
    
  def stop(self):
    self._stopped = True
  
class Worker(StoppableThread):
  def __init__(self, queue, filekeeper, metastore, thread_id):
    StoppableThread.__init__(self)
    self.metastore = metastore
    self.filekeeper = filekeeper
    self.thread_id = thread_id
    self.queue = queue
    self.performing_task = None
    self.state = 'initializing'
    
  def performTask(self, task):
    self.performing_task = task
    
    # Creating new store
    store = Store(task.index_fields)

    # Reading data
    self.state = 'reading data from log %s' % task.log
    data = self.filekeeper.read(task.log)
    logging.debug("[worker %s] read %d bytes from %s" % (task.collector_name, len(data), task.log))

    # Parsing and pushing data
    self.state = 'parsing data from log %s' % task.log
    total = 0
    parsed = 0
    for line in data.split('\n'):
      record = task.parser.parseLine(line)
      if task.parser.successful:
        parsed += 1
        store.push(record)
      total += 1
    logging.info('[worker %s] parsed %d of %d lines of %s' % (task.collector_name, parsed, total, task.log))
    store.reindexAll()
    
    # Storing data to Watcher tables
    self.metastore[task.collector_name] = store
    
    # TODO variables
    
    self.performing_task = None
    task.setDone()
  
  def __repr__(self):
    return "[Worker #%s %s]" % (self.thread_id, self.state)
    
  def run(self):
    while not self._stopped:
      self.state = 'sleeping'
      # sleeping up to 100ms for cpu idle
      time.sleep(random.random()/10)
      self.state = 'getting task from queue'
      try:
        task = self.queue.get_nowait()
      except Queue.Empty:
        continue
      self.performTask(task)
  
  
class Scheduler(StoppableThread):
  def __init__(self, tasks, filekeeper, metastore, numThreads=10):
    StoppableThread.__init__(self)
    self._stopped = False
    self.filekeeper = filekeeper
    self.tasks = tasks
    self.queue = Queue.Queue()
    self.pool = []
    for i in xrange(numThreads):
      worker = Worker(self.queue, self.filekeeper, metastore, i+1)
      self.pool.append(worker)
  
  def stop(self):
    for worker in self.pool:
      worker.stop()
    StoppableThread.stop(self)

  def run(self):
    for worker in self.pool:
      worker.start()
    while not self._stopped:
      time.sleep(1.0)
      for task in self.tasks:
        if task.isReady():
          logging.debug("[scheduler] Task %s put to queue" % task)
          self.queue.put(task.setQueued())
