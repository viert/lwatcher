#!/usr/bin/env python

from optparse import OptionParser
from lwlib.yamlreader import ConfigReader
from lwlib.parser import LogParser
import sys

op = OptionParser()
op.add_option("-c", "--config", dest="configfile", help="Use config FILE", type="string")
(options,args) = op.parse_args()
if options.configfile is None:
  print "Config filename is missing"
  print "Use inparse.py -c FILE"
  sys.exit(1)

c = ConfigReader(options.configfile)
parser = LogParser(c.config['parser'])
while True:
  line = sys.stdin.readline()
  
  if line == '':
    break

  fields = parser.parseLine(line)
  if parser.successful:
    print repr(fields)
  else:
    print "FAILED TO PARSE"
