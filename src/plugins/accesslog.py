#!/usr/bin/env python

from collections import Counter

def CountRPSbyVhost(store):
  "needs @vhost field indexed"
  return store.indexes['vhost']['counter']

def Count500byVhost(store):
  "needs @status:@vhost index"
  return store.indexes['status.vhost']['counter']['500']

exports = [Count500byVhost, CountRPSbyVhost]
