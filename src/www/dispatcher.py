#!/usr/bin/env python

from lwlib import Watcher
from flask import Flask, make_response, request
import sys

watcher = Watcher('./conf', 'testwatcher.log', './plugins')
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
def data(table_name=None):
  result = ""
  if not table_name in watcher.tables.keys():
    resp = make_response("404 table not found", 404)
    return resp
  
  i = 0
  for record in watcher.tables[table_name].table:
    result += repr(record) + "\n"
    i+=1
    
  result += "\nTotal: %d records\n" % i
  resp = make_response(result, 200)
  resp.headers['Content-Type'] = 'text/plain'
  return resp
  
