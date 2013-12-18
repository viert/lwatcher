#!/usr/bin/env python

import yaml

def unescape(string):
  return string.replace("\\n", "\n").replace("\\t", "\t")

class ConfigReader(object):
  def __init__(self, filename):
    self.configfilename = filename
    self.config = {}
    self.config['options'] = {}
    self.config['vars'] = {}
    self.config['parser'] = []
    self.__parse()
    
  def __parse(self):
    f = open(self.configfilename)
    raw = yaml.load(f.read())
    f.close()
    
    self.config['options'] = raw['config']
    self.config['options']['deviation'] = 0.05 * self.config['options']['period']
    
    for raw_directive in raw['parser']['directives']:
      directive = []
      cmd = raw_directive.keys()[0]
      
      args = raw_directive[cmd]
      if type(args) == str:
        args = [args]
      args = [unescape(x) for x in args]
      
      directive.append(cmd)
      directive += args
      self.config['parser'].append(directive)
    
    if 'vars' in raw.keys():  
      for varname in raw['vars'].keys():
        raw_var = raw['vars'][varname]
        if type(raw_var) == str:
          raw_var = [raw_var]
        self.config['vars'][varname] = raw_var