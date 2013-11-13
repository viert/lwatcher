#!/usr/bin/env python

from lwlib import ConfigReader, LogParser

c = ConfigReader("conf/example.conf")
p = LogParser(c.config['parser'])
f = open("/var/log/syslog")
for line in f.readlines():
  print repr(p.parseLine(line))
f.close()
