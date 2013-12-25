#!/usr/bin/env python

import dateutil.parser
import datetime
import logging

def convertToDatetime(record, key, format=None):
  if format is None:
    dt = dateutil.parser.parse(record[key])
  else:
    dt = datetime.datetime.strptime(record[key], format)
  record[key] = dt
  
def convertToFloat(record, key, default=None):
  try:
    record[key] = float(record[key])
  except ValueError:
    if not default is None:
      record[key] = default

def convertToInt(record, key, default=None, base=10):
  try:
    record[key] = int(record[key], base)
  except ValueError:
    if not default is None:
      record[key] = default

# backward compatibility function
def convertDate(*args):
  return convertToDatetime(args)

exports = [convertDate, convertToFloat, convertToInt, convertToDatetime]