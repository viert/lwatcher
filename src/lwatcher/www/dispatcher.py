#!/usr/bin/env python

from lwatcher.lwlib import Watcher
from flask import Flask, make_response, request
import json
import sys

CONFIG_DIR = '/etc/lwatcher'
PLUGINS_DIR = '/usr/lib/lwatcher/plugins'
LOG_FILE = '/var/log/lwatcher/lwatcher.log'

watcher = Watcher(CONFIG_DIR, LOG_FILE, PLUGINS_DIR)
app = Flask('WatcherApplication')

def startApplication():
  watcher.start()
  app.run()

@app.route('/')
def index():
  result = "=== Worker stats ===\n\n"
  for worker in watcher.scheduler.pool:
    result += repr(worker) + "\n"
  result += "\n"
  
  result += "=== Tasks ===\n\n"
  for task in watcher.tasks:
    result += repr(task) + "\n"
  result += "\n"
  
  result += "=== Tables ===\n\n"
  for key in watcher.tables.keys():
    result += key + "\n"

  result += "\n"
  result += "=== Functions ===\n\n"
  for key in watcher.functions.keys():
    doc = watcher.functions[key].__doc__
    result += key
    if len(doc) > 0:
      result += "\n"
      for line in doc.split("\n"):
        result += "    " + line + "\n"
    result += "\n"
    
  resp = make_response(result, 200)
  resp.headers['Content-Type'] = 'text/plain'
  return resp

@app.route('/data/<table_name>')
@app.route('/data/<table_name>/<var_name>')
def data(table_name=None, var_name=None):
  if table_name is None:
    return make_response('Bad request', 400)
  
  if not table_name in watcher.tables.keys():
    return make_response("Table not found", 404)

  if var_name is None:
    result = { 'total' : len(watcher.tables[table_name].table), 'data' : watcher.tables[table_name].table }
    resp = make_response(json.dumps(result), 200)
    resp.headers['Content-Type'] = 'application/json'
    return resp
  else:
    if not var_name in watcher.tables[table_name].vars.keys():
      return make_response("Variable not found", 404)
    else:
      resp = make_response(json.dumps(watcher.tables[table_name].vars[var_name]), 200)
      resp.headers['Content-Type'] = 'application/json'
      return resp
