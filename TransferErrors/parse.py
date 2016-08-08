#!/usr/bin/env python

import common
import json
from time import time

def parseBlockArrive(bufferpath_tmpl='',skip=[0]):
  '''
  bufferpath_tmpl contain %s => ..., m2, m1, 0, 1,...
  '''
  if bufferpath_tmpl=='':
    bufferpath_tmpl = common.tmpdir+'blockarrive_%s.json'

  stuckDatasets = {}

  for iB in xrange(-6,3):
    if iB in skip:
      continue
    payload = common.getJson(bufferpath_tmpl%(str(iB).replace('-','m')))
    if not payload:
      continue
    for block in payload['block']:
      blockname = block['name']
      datasetname = block['dataset']
      try:
        dataset = stuckDatasets['datasetname']
      except KeyError:
        dataset = common.TMDBDataset(datasetname)
        stuckDatasets[datasetname] = dataset
      try:
        stuckBlock = dataset.stuckBlocks[blockname]
      except KeyError:
        stuckBlock = common.TMDBBlock(blockname)
        dataset.stuckBlocks[blockname] = stuckBlock
      for dest in block['destination']:
        stuckBlock.targets.add((dest['name'],iB))

  return stuckDatasets 

def filterSubscriptions(stuckDatasets,bufferpath='',threshold=7):
  if bufferpath=='':
    bufferpath_sub = common.tmpdir+'subscription.json'
    bufferpath_mis = common.tmpdir+'missingfiles.json'
  api_sub = common.APIHandler(which='subscriptions',method='wget')
  api_mis = common.APIHandler(which='missingfiles',method='wget')
  now = time()
  emptyDatasets=set([])
  for dsname,ds in stuckDatasets.iteritems():
    emptyBlocks=set([])
    for blockname,block in ds.stuckBlocks.iteritems():
      # first check when subscription was made
      flags = ' -O %s'%bufferpath_sub
      toRemove = set([])
      for t in block.targets:
        if 'X' in t[0]:
          toRemove.add(t)
          continue
        time_create = now
        params = {'node':t[0], 'block':block.name.replace('#','%23')}
        api_sub(params,flags)
        payload = common.getJson(bufferpath_sub)['dataset']
        try:
          time_create = int(payload[0]['block'][0]['subscription'][0]['time_create'])
        except KeyError:
          time_create = int(payload[0]['subscription'][0]['time_create'])
        if time_create-now < threshold*common.sPerDay:
          toRemove.add(t)
          continue
      for t in toRemove:
        block.targets.remove(t)
      if len(block.targets)==0:
        emptyBlocks.add(blockname)
    for blockname in emptyBlocks:
      del ds.stuckBlocks[blockname]
    if len(ds.stuckBlocks)==0:
      emptyDatasets.add(dsname)
  for dsname in emptyDatasets:
    del stuckDatasets[dsname]



