#!/usr/bin/env python

from collections import Counter
import datetime, re, logging

COMPILED_RE = {}

def CountRPSbyVhost(store):
  "needs @vhost and @datetime field indexed"
  dtkeys = store.indexes['datetime']['sortedkeys']
  if not dtkeys:
    return None
  tmin = dtkeys[0]
  tmax = dtkeys[len(dtkeys)-1]
  tdelta = (tmax - tmin).seconds
  
  rps = {}
  for k, v in store.indexes['vhost']['counter'].items():
    rps[k] = float(v) / tdelta
  
  rps['_total'] = sum(rps.values())
  return rps

def Count500byVhost(store):
  "needs @status:@vhost index"
  return store.indexes['status.vhost']['counter']['500']

def DiscreteTimings(store, url_filter=None):
  if url_filter in COMPILED_RE:
    regexp = COMPILED_RE[url_filter]
  else:
    try:
      regexp = re.compile(url_filter)
      COMPILED_RE[url_filter] = regexp
    except:
      logging.error('Invalid RegExp: "%s"' % url_filter)
      return {}
  result = Counter()
  invalid_time = 0
  count = 0
  for record in store:
    count += 1
    if regexp.search(record['url']):
      try:
        timing = int(record['time']*1000)/10
      except:
        invalid_time += 1
      result[timing] += 1
      
  if invalid_time:
    logging.error('Invalid timings found (%d of %d). Are you still store "time" as string?' % (invalid_time, count))
  return result
  

exports = [Count500byVhost, CountRPSbyVhost, DiscreteTimings]
