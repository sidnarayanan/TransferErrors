#!/usr/bin/env python

import common
from time import time
import os

def getBlockArrive(refresh=False,bufferPath_tmpl='',skip=[0]):
  if bufferPath_tmpl=='':
    bufferPath_tmpl = common.tmpdir+'blockarrive_%s.json'
  for iB in xrange(-6,3):
    if iB in skip:
      continue
    bufferPath = bufferPath_tmpl%(str(iB).replace('-','m'))
    if not refresh:
      if os.path.isfile(bufferPath) and (os.path.getmtime(bufferPath)-time() < common.sPerDay):
        continue
    flags = ' --no-check-certificate -O %s'%bufferPath
    url = '"https://cmsweb.cern.ch/phedex/datasvc/json/prod/blockarrive?block=*&basis=%i"'%(iB)
    cmd = 'wget %s %s'%(flags,url)
    print cmd
    os.system(cmd) 