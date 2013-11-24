#!/usr/bin/env python

import os

class FileKeeper(object):
  def __init__(self):
    self.filestore = {}
  
  def read(filename):
    data = ''
    
    if filename in self.filestore.keys():
      (stat, f) = self.filestore[filename]
      
      
      # At this point nothing could happen with already opened file even if someone deleted it.
      # Read it to the end
      data = f.read()

      try:
        new_stat = os.stat(filename)
      except OSError:
        # We reach here if file was removed or renamed and no file was created in his place
        # Maybe someone is still writing file in (deleted) state, giving up
        return data
      
      if new_stat.st_ino != stat.st_ino:
        # We reach here after logrotate for example: file was moved or deleted and another one is in his place
        f.close()
        try:
          f = open(filename)
        except OSError:
          # Rare case when someone deleted file after our last access
          del(self.filestore[filename])
          return data
        # Reading the new file to the end
        data += f.read()
      
      return data
      
    else:
      # first time file access
      try:
        f = open(filename, "r")
        stat = os.stat(filename)
      except OSError:
        # if file doesn't exist just do nothing, hoping the file to appear next time
        return ''
      # first time access doesn't contain any data, next time we'll read it from this very place
      f.seek(stat.st_size-1)
      self.filestore[filename] = (stat, f)
      return ''