#!/usr/bin/env python

import random, time, threading, Queue

class Task(object):
  def __init__(self, collector_name, log, parser, variables, period, dispersion, store):
    self.collector_name = collector_name
    self.parser = parser
    self.log = log
    self.variables = variables
    self.period = period
    self.dispersion = dispersion
    self.store = store
    self.doneAt = None
    self.setNextStart()
    
  def setNextStart(self):
    if self.doneAt is None:
      # first time start in min dispersion seconds
      self.nextStart = time.time() + random.randint(0, self.dispersion)
    else:
      deviation = random.randint(-self.dispersion, self.dispersion)
      self.nextStart = self.doneAt + self.period + deviation
  
  def isReady(self):
    return time.time() >= self.nextStart



class StoppableThread(threading.Thread):
  def __init__(self):
    self.__stopped = False
    threading.Thread.__init__(self)
    
  def stop(self):
    self.__stopped = True


  
class Worker(StoppableThread):
  def __init__(self, queue):
    StoppableThread.__init__(self)
    self.queue = queue
    self.performing_task = None
    self.state = 'initializing'
    
  def performTask(self, task):
    self.performing_task = task
    # TODO
    
    self.performing_task = None    
  
  def __repr__(self):
    return "<Worker %d>" % threading.Thread.ident
    
  def run(self):
    while not self.__stopped:
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
  def __init__(self, tasks, numThreads=10):
    StoppableThread.__init__(self)
    self.__stopped = False
    self.tasks = tasks
    self.queue = Queue()
    self.pool = []
    for i in xrange(numThreads):
      worker = Worker(self.queue)
      worker.start()
      self.pool.append(worker)
  
  def run(self):
    while not self.__stopped:
      time.sleep(1.0)
      for task in self.tasks:
        if task.isReady():
          self.queue.put(task)
