#!/usr/bin/env python

from collections import Counter


def CountRPSbyVhost(store):
  "needs @vhost field indexed"
  return store.indexes['vhost']['counter']

def Count500byVhost(store):
  "needs @status:@vhost index"
  result = Counter()
  for key in store.indexes['status:vhost']['counter']:
    if key.startswith('500:'):
      vhost = key[4:]
      result[vhost] += 1
  return result

exports = [Count500byVhost, CountRPSbyVhost]
