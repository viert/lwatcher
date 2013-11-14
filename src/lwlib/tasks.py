#!/usr/bin/env python

import random, time, threading

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
  
class Worker(threading.Thread):
  def __init__(self, store):
    self.store = store
    
  
  
class Scheduler(object):
  def __init__(self, tasks):
    self.tasks = tasks
    
