#!/usr/bin/env python

import common
from time import time
import os

def getBlockArrive(refresh=False,bufferpath_tmpl='',skip=[0]):
  if bufferpath_tmpl=='':
    bufferpath_tmpl = common.tmpdir+'blockarrive_%s.json'
  api = common.APIHandler(which='blockarrive',method='wget')
  api.VERBOSE=True
  for iB in xrange(-6,3):
    if iB in skip:
      continue
    bufferpath = bufferpath_tmpl%(str(iB).replace('-','m'))
    if not refresh:
      if os.path.isfile(bufferpath) and (time()-os.path.getmtime(bufferpath) < common.sPerDay):
        continue
    flags = '-O %s'%bufferpath
    params = {'basis':iB}
    api(params,flags)

def getErrorLogs(refresh=False,bufferpath_tmpl='',skip=[]):
  if bufferpath_tmpl=='':
    bufferpath_tmpl = common.tmpdir+'errorlog_%s.json'
  api = common.APIHandler(which='errorlog',method='wget')
  api.VERBOSE=True
  for site in common.siteNames:
    if site in skip:
      continue
    bufferpath = bufferpath_tmpl%(site)
    if not refresh:
      if os.path.isfile(bufferpath) and (time()-os.path.getmtime(bufferpath) < common.sPerDay):
        continue
    flags = '-O %s'%bufferpath
    params = {'to':site}
    api(params,flags)

def getSubscriptions(refresh=False,bufferpath_tmpl='',window=60):
  # window is number of days back to look
  dspattern = os.getenv('DATASETPATTERN')
  if bufferpath_tmpl=='':
    bufferpath_tmpl = common.tmpdir+'subs.json'
  since = time()-window*common.sPerDay
  if window==0:
    since = 1
  if not refresh:
      if os.path.isfile(bufferpath_tmpl) and (time()-os.path.getmtime(bufferpath_tmpl) < common.sPerDay):
        return
  api = common.APIHandler(which='subscriptions',method='wget')
  api.VERBOSE=True
  flags = ' -O %s'%bufferpath_tmpl
  params = {'create_since':int(since), 'block':'%s%%23*'%(dspattern), 'collapse':'n','percent_max':100}
  api(params,flags)
