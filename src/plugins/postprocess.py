#!/usr/bin/env python

import dateutil.parser
import datetime
import logging

def convertDate(record, key, format=None):
  if format is None:
    dt = dateutil.parser.parse(record[key])
  else:
    dt = datetime.datetime.strptime(record[key], format)
  record[key] = dt

exports = [convertDate]