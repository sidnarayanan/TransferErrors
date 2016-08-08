#!/usr/bin/env python

import common
from time import time
import os

def getBlockArrive(refresh=False,bufferPath_tmpl='',skip=[0]):
  if bufferPath_tmpl=='':
    bufferPath_tmpl = common.tmpdir+'blockarrive_%s.json'
  api = common.APIHandler(which='blockarrive',method='wget')
  api.VERBOSE=True
  for iB in xrange(-6,3):
    if iB in skip:
      continue
    bufferPath = bufferPath_tmpl%(str(iB).replace('-','m'))
    if not refresh:
      if os.path.isfile(bufferPath) and (os.path.getmtime(bufferPath)-time() < common.sPerDay):
        continue
    flags = '-O %s'%bufferPath
    params = {'basis':iB}
    api(params,flags)

def getErrorLogs(refresh=False,bufferPath_tmpl='',skip=[]):
  if bufferPath_tmpl=='':
    bufferPath_tmpl = common.tmpdir+'errorlog_%s.json'
  api = common.APIHandler(which='errorlog',method='wget')
  api.VERBOSE=True
  for site in common.siteNames:
    if site in skip:
      continue
    bufferPath = bufferPath_tmpl%(site)
    if not refresh:
      if os.path.isfile(bufferPath) and (os.path.getmtime(bufferPath)-time() < common.sPerDay):
        continue
    flags = '-O %s'%bufferPath
    params = {'to':site}
    api(params,flags)