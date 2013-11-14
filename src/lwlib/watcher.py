#!/usr/bin/env python

from configreader import ConfigReader
from tasks import Task, Scheduler
from parser import LogParser
from store import Store
import os
import logging


class Watcher(object):

  def __init__(self, config_directory, log_filename):
    self.config_directory = config_directory
    logging.basicConfig(filename=log_filename, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    self.tables = {}
    self.reconfigureTasks()
    self.scheduler = Scheduler(self.tasks)
    
  def reconfigureTasks(self):
    self.tasks = []
    for f in os.listdir(self.config_directory):
      try:
        c = ConfigReader(self.config_directory + "/" + f)
      except Exception as e:
        logging.error('Error reading config file %s: %s' % (f, repr(e)))

      if 'c' in locals():
        collector_name = c.config['options']['name']
        index_fields = []
        for directive in c.config['parser']:
          if directive[0] == 'index':
            index_fields.append(directive[1])
        self.tables[collector_name] = Store(index_fields)
        task = Task(collector_name, c.config['options']['log'], LogParser(c.config['parser']), c.config['vars'], c.config['options']['period'], c.config['options']['deviation'], self.tables[collector_name])
        self.tasks.append(task)
