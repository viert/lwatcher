#!/usr/bin/env python

import os
import logging

class FileKeeper(object):
  def __init__(self):
    self.filestore = {}
  
  def read(self, filename):
    data = ''
    
    if filename in self.filestore.keys():
      logging.debug('file "%s" metadata found in filestore' % filename)
      (stat, f) = self.filestore[filename]
      
      logging.debug('file "%s" stat: %s' % (filename, str(stat)))
      # At this point nothing could happen with already opened file even if someone deleted it.
      # Read it to the end
      data = f.read()

      try:
        new_stat = os.stat(filename)
        logging.debug('got new stat: %s' % str(new_stat))
      except OSError, e:
        logging.debug('got OSError while getting new_stat for %s: %s' % (filename, str(e)))
        # We reach here if file was removed or renamed and no file was created in his place
        # Maybe someone is still writing file in (deleted) state, giving up
        return data
      
      if new_stat.st_ino != stat.st_ino or new_stat.st_size < f.tell():
        # We reach here after logrotate for example: file was moved or deleted and another one is in his place or file was zeroed
        f.close()
        del(self.filestore[filename])
        logging.debug('new_stat inode != old_stat inode')

        try:
          logging.debug('opening new stated file')
          f = open(filename)
        except OSError, e:
          logging.debug('got OSError while opening new file %s: %s' % (filename, str(e)))
          # Rare case when someone deleted file after our last access
          return data

        # Reading the new file to the end
        
        data += f.read()
        self.filestore[filename] = (new_stat, f)
        logging.debug('new_stat and file descriptor saved')
      
      return data
      
    else:
      # first time file access
      logging.debug('first time file access for "%s"' % filename)
      try:
        f = open(filename, "r")
        stat = os.stat(filename)
      except OSError, e:
        logging.debug('got OSError while opening new file %s: %s' % (filename, str(e)))
        # if file doesn't exist just do nothing, hoping the file to appear next time
        return ''
      # first time access doesn't contain any data, next time we'll read it from this very place
      logging.debug('seeking to the end of %s' % filename)
      f.seek(stat.st_size)
      self.filestore[filename] = (stat, f)
      logging.debug('stat and file descriptor saved')
      return ''