#!/usr/bin/env python

from lwatcher.lwlib import Watcher
from lwatcher.daemontools import *
from flask import Flask, make_response, request
from ConfigParser import ConfigParser
import json, sys, datetime, logging, os

CONFIG_DIR = '/etc/lwatcher'
CONFIG_FILE = CONFIG_DIR + '/lwatcher.conf'
COLLECTOR_CONFIG_DIR = '/etc/lwatcher/collectors'
PLUGINS_DIR = '/usr/lib/lwatcher/plugins'
LOG_FILE = '/var/log/lwatcher/lwatcher.log'
LOG_LEVEL = 'DEBUG'
PID_FILE = '/var/run/lwatcher.pid'
BIND_HOST = '127.0.0.1'
BIND_PORT = 5000
THREADS_NUM = 10

cp = ConfigParser({ 'pid_file' : PID_FILE, 'log_file' : LOG_FILE, 'threads' : THREADS_NUM, 'bind_host' : BIND_HOST, 'bind_port' : BIND_PORT, 'plugin_dir' : PLUGINS_DIR, 'log_level' : LOG_LEVEL })
try:
  cp.readfp(open(CONFIG_FILE))
except Exception, e:
  print "Error reading config file: " + repr(e)
  sys.exit(1)

logfile     = cp.get('main', 'log_file')
plugin_dir  = cp.get('main', 'plugin_dir')
bind_host   = cp.get('main', 'bind_host')
bind_port   = cp.getint('main', 'bind_port')
threads     = cp.getint('main', 'threads')
pidfile     = cp.get('main', 'pid_file')
logdir      = os.path.dirname(logfile)
try:
  loglevel    = logging.__getattribute__(cp.get('main', 'log_level').upper())
except AttributeError:
  loglevel    = logging.__getattribute__(LOG_LEVEL)

watcher = Watcher(COLLECTOR_CONFIG_DIR, logfile, plugin_dir, threads, loglevel)
app = Flask('WatcherApplication')

def __startApplication():
  watcher.start()
  app.run(host=bind_host, port=bind_port)
  
def startApplicationAsDaemon():
  os.closerange(0,3)
  sys.stdout = open('%s/stdout.log' % logdir, "a")
  sys.stderr = open('%s/stderr.log' % logdir, "a")
  startDaemon(__startApplication, pidfile)

def jsonFixer(obj):
  if isinstance(obj, datetime.datetime):
    return obj.isoformat()
  else:
    return obj

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
    if doc and len(doc) > 0:
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
    resp = make_response(json.dumps(result, default=jsonFixer), 200)
    resp.headers['Content-Type'] = 'application/json'
    return resp
  else:
    if not var_name in watcher.tables[table_name].vars.keys():
      return make_response("Variable not found", 404)
    else:
      resp = make_response(json.dumps(watcher.tables[table_name].vars[var_name], default=jsonFixer), 200)
      resp.headers['Content-Type'] = 'application/json'
      return resp
