#!/usr/bin/env python

import random, time, threading, Queue
import logging
import datetime
from store import Store

class Task(object):
  def __init__(self, collector_name, log, parser, variables, period, dispersion, index_fields, after_parse_callbacks):
    self.collector_name = collector_name
    self.parser = parser
    self.log = log
    self.variables = variables
    self.period = period
    self.dispersion = dispersion
    self.index_fields = index_fields
    self.after_parse_callbacks = after_parse_callbacks
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
    doneAt = datetime.datetime.fromtimestamp(self.doneAt).strftime('%H:%M:%S')
    nextStart = datetime.datetime.fromtimestamp(self.nextStart).strftime('%H:%M:%S')
    return "[Task collector_name=%s log=%s processing=%s doneAt=%s nextStart=%s]" % (self.collector_name, self.log, self.processing, doneAt, nextStart)
  
  
  def isReady(self):
    return not self.processing and (time.time() >= self.nextStart)

class StoppableThread(threading.Thread):
  def __init__(self):
    self._stopped = False
    threading.Thread.__init__(self)
    self.state = 'initializing'
    self.daemon = True
    
  def stop(self):
    self.state = 'stopping'
    self._stopped = True

  
class Worker(StoppableThread):
  def __init__(self, queue, filekeeper, metastore, functions, thread_id):
    StoppableThread.__init__(self)
    self.metastore = metastore
    self.filekeeper = filekeeper
    self.functions = functions
    self.thread_id = thread_id
    self.queue = queue
    self.performing_task = None
    
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
    t1 = time.time()
    for line in data.split('\n'):
      record = task.parser.parseLine(line+'\n')
      if task.parser.successful:
        parsed += 1
        # after_parse_callbacks
        for callback in task.after_parse_callbacks:
          func = callback[0]
          args = [record] + callback[1:]
          try:
            func(*args)
          except Exception, e:
            logging.debug('[%s.%s] %s' % (func.__module__, func.__name__, repr(e)))
        store.push(record)
      total += 1
    t2 = time.time()
    logging.info('[worker %s] parsed %d of %d lines of %s in %.02f seconds' % (task.collector_name, parsed, total, task.log, t2-t1))
    store.reindexAll()
    t3 = time.time()
    logging.info('[worker %s] indexes built in %.02f seconds' % (task.collector_name, t3-t2))
    
    
    self.state = 'calculating functions for log %s' % task.log
    for var in task.variables:
      
      varname, funcname = var, task.variables[var][0]

      # TODO args
      if len(task.variables[var]) > 1:
        args = task.variables[var][1:]
      else:
        args = []
      
      if not funcname in self.functions.keys():
        logging.error("No function \"%s\" found in registered plugins" % funcname)
        continue
      else:
        try:
          result = self.functions[funcname](store, *args)
        except Exception, e:
          logging.debug("[%s] %s" % (funcname, repr(e)))
          continue
        store.setVar(varname, result)
    t4 = time.time()
    logging.info('[worker %s] functions calculated in %.02f seconds' % (task.collector_name, t4-t3))
    
    # Storing data to Watcher tables
    self.metastore[task.collector_name] = store
    
    logging.info('[worker %s] task done in %.02f seconds' % (task.collector_name, t4-t1))

    self.performing_task = None
    task.setDone()
  
  def __repr__(self):
    return "[Worker #%s %s]" % (self.thread_id, self.state)
    
  def run(self):
    try:
      while not self._stopped:
        self.state = 'sleeping'
        # sleeping up to 250ms for cpu idle
        time.sleep(random.random()/4)
        self.state = 'getting task from queue'
        try:
          task = self.queue.get_nowait()
        except Queue.Empty:
          continue
        self.performTask(task)
    except:
      self.stop()
    self.state = 'stopped'
  
  
class Scheduler(StoppableThread):
  def __init__(self, tasks, filekeeper, metastore, functions, numThreads=10):
    StoppableThread.__init__(self)
    self._stopped = False
    self.filekeeper = filekeeper
    self.tasks = tasks
    self.queue = Queue.Queue()
    self.pool = []
    for i in xrange(numThreads):
      worker = Worker(self.queue, self.filekeeper, metastore, functions, i+1)
      self.pool.append(worker)
  
  def stop(self):
    for worker in self.pool:
      worker.stop()
    StoppableThread.stop(self)

  def run(self):
    self.state = 'running'
    try:
      for worker in self.pool:
        worker.start()
      while not self._stopped:
        time.sleep(1.0)
        for task in self.tasks:
          if task.isReady():
            logging.debug("[scheduler] Task %s put to queue" % task)
            self.queue.put(task.setQueued())
    except:
      self.stop()
    self.state = 'stopped'
