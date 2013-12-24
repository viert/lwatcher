#!/usr/bin/env python

from collections import Counter
import datetime

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

exports = [Count500byVhost, CountRPSbyVhost]
