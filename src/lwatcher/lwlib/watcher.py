#!/usr/bin/env python

from yamlreader import ConfigReader
from tasks import Task, Scheduler
from parser import LogParser
from store import Store
from filekeeper import FileKeeper
import os, logging, sys

class Watcher(object):

  def __init__(self, config_directory, log_filename, plugin_directory):
    self.config_directory = config_directory
    self.plugin_directory = plugin_directory
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    self.functions = {}
    self.tables = {}
    self.importPlugins()
    self.reconfigureTasks()
    self.filekeeper = FileKeeper()
    self.scheduler = Scheduler(self.tasks, self.filekeeper, self.tables, self.functions)

  def start(self):
    self.scheduler.start()

  def stop(self):
    self.scheduler.stop()

  def importPlugins(self):
    sys.path.append(self.plugin_directory)
    for python_file in os.listdir(self.plugin_directory):
      module_name = os.path.splitext(os.path.basename(python_file))[0]
      try:
        i = __import__(module_name)
      except ImportError, e:
        logging.warn('Error importing module "%s": %s' % (module_name, repr(e)))
        continue
      try:
        exports = i.exports
      except AttributeError, e:
        logging.warn('Error importing module "%s": %s' % (module_name, repr(e)))
        continue
      for func_name in exports:
        if hasattr(func_name, '__call__'):
          # exported function itself
          func = func_name
          func_name = func.__name__
        else:
          try:
            func = i.__dict__[func_name]
          except KeyError, e:
            logging.warn('Error importing function "%s" from module "%s"' % (module_name, func_name))
            continue
        key = '.'.join([module_name, func_name])
        self.functions[key] = func

  def reconfigureTasks(self):
    self.tasks = []
    for f in os.listdir(self.config_directory):
      if os.path.isdir(self.config_directory + '/' + f):
        continue
      try:
        c = ConfigReader(self.config_directory + "/" + f)
      except Exception as e:
        logging.error('Error reading config file %s: %s' % (f, repr(e)))

      if 'c' in locals():
        collector_name = c.config['options']['name']
        index_fields = []
        after_parse_callbacks = []
        for directive in c.config['parser']:
          if directive[0] == 'index':
            index_fields.append(directive[1])
          elif directive[0] == 'afterParse':
            try:
              callback = [self.functions[directive[1]]]
            except KeyError, e:
              logging.error('No function %s found for afterParse callback in config file %s' % (directive[1], f))
            callback += directive[2:]
            after_parse_callbacks.append(callback)
            
        # empty store
        self.tables[collector_name] = Store(index_fields)
        
        task = Task(collector_name, c.config['options']['log'], LogParser(c.config['parser']), c.config['vars'], c.config['options']['period'], c.config['options']['deviation'], index_fields, after_parse_callbacks)
        self.tasks.append(task)
