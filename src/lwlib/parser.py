#!/usr/bin/env python

import Tokenparser

class Parser(object):
  def __init__(self, directives):
    self.p = Tokenparser()
    self.directives = directives
    for d in self.directives:
      dname = d[0]
      args = d[1:]

      if dname == 'skip':
        p.skip(*args)
      elif dname == 'skipTo':
        p.skipTo(*args)
      elif dname == 'upTo':
        p.upTo(args[1], args[0])
        if len(args) > 2:
          pass # TODO types
      elif dname == 'fromTo':
        p.fromTo(args[2], args[0], args[1])
        if len(args) > 3:
          pass # TODO typesl
        
      