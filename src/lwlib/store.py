#!/usr/bin/env python

from collections import defaultdict, Counter

class Store(object):
  def __init__(self, index_fields=[]):
    self.table = []
    self.indexes = {}
    for field in index_fields:
      self.addIndex(field)

  def fields(self):
    if len(self.table) == 0:
      return []
    else:
      return self.table[0].keys()
    
  def addIndex(self, field):
    if not field in self.indexes.keys():
      self.indexes[field] = {}
      self.clearIndex(field)
  
  def removeIndex(self, field):
    if field in self.indexes.keys():
      del(self.indexes['field'])
  
  def clearIndex(self, field):
    keyparts = field.split('.')
    if len(keyparts) == 1:
      self.indexes[field]['index'] = defaultdict(list)
      self.indexes[field]['counter'] = Counter()
    elif len(keyparts) == 2:
      self.indexes[field]['index'] = defaultdict(lambda: defaultdict(list))
      self.indexes[field]['counter'] = defaultdict(Counter)
    else:
      raise NotImplementedError('Complex indexes of three and more fields are not implemented')
  
  def clearIndexes(self):
    for field in self.indexes.keys():
      self.clearIndex(field)
  
  def reindexAll(self):
    for field in self.indexes.keys():
      self.reindex(field)
      
  def reindex(self, field):
    self.clearIndex(field)
    keyparts = field.split('.')
    c = 0
    
    if len(keyparts) == 1:
      for record in self.table:
        self.indexes[field]['index'][record[field]].append(c)
        self.indexes[field]['counter'][record[field]] += 1
        c += 1
    else:
      (first, second) = keyparts
      for record  in self.table:
        self.indexes[field]['index'][record[first]][record[second]].append(c)
        self.indexes[field]['counter'][record[first]][record[second]] += 1
        c += 1
        

  def clearAll(self):
    self.clearIndexes()
    self.table = []

  def push(self, record):
    self.table.append(record)
    
  