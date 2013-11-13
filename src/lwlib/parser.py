#!/usr/bin/env python

import Tokenparser

class LogParser(object):
  def __init__(self, directives):
    self.p = Tokenparser.Tokenparser()
    self.directives = directives
    for d in self.directives:
      dname = d[0]
      args = d[1:]
      
      if dname == 'skip':
        self.p.skip(*args)
      elif dname == 'skipTo':
        self.p.skipTo(*args)
      elif dname == 'upTo':
        self.p.upTo(args[1], args[0])
        if len(args) > 2:
          pass # TODO types
      elif dname == 'fromTo':
        self.p.fromTo(args[2], args[0], args[1])
        if len(args) > 3:
          pass # TODO types
    self.resetCounters()
    self.successful = False
    self.result = None
    
  def resetCounters(self):
    self.total = 0
    self.parsed = 0
    self.failed = 0
      
  def parseLine(self, line):
    self.p.clearMatches()
    self.total += 1
    if not self.p.parse(line):
      self.failed += 1
      self.successful = False
      self.result = None
      return {}
    else:
      self.parsed += 1
      self.successful = True
      self.result = self.p.matches()
      return self.p.matches()
