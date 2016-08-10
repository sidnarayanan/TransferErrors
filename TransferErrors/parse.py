#!/usr/bin/env python

import common
import json
from time import time
import pprint

def parseBlockArrive(bufferpath_tmpl='',skip=[0],threshold=0):
  '''
  bufferpath_tmpl contain %s => ..., m2, m1, 0, 1,...
  only consider blocks at least threshold [days] old (to avoid new stuff)
  '''
  if bufferpath_tmpl=='':
    bufferpath_tmpl = common.tmpdir+'blockarrive_%s.json'

  stuckDatasets = {}
  now = time()

  for iB in xrange(-6,3):
    if iB in skip:
      continue
    payload = common.getJson(bufferpath_tmpl%(str(iB).replace('-','m')))
    if not payload:
      continue
    for block in payload['block']:
      blockname = block['name']
      datasetname = block['dataset']
      time_create = block['time_create']
      if now-time_create < threshold*common.sPerDay:
        continue 
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
      stuckBlock.volume = block['bytes']
      for dest in block['destination']:
        stuckBlock.targets.add(common.Subscription(dest['name'],iB))

  return stuckDatasets 

def filterSubscriptions(stuckDatasets,bufferpath='',threshold=7):
  if bufferpath=='':
    bufferpath = common.tmpdir+'subs.json'
  now = time()
  threshold *= common.sPerDay

  # parse the subscriptions
  payload = common.getJson(bufferpath)['dataset']
  subscriptions = {} # dataset : {block:[common.Subscription]}
  for d in payload:
    dname = d['name']
    if not (dname in subscriptions):
      subscriptions[dname] = {}
    # dataset-level
    # pprint.pprint(d)
    if 'subscription' in d:
      for s in d['subscription']:
        if not('' in subscriptions[dname]):
          subscriptions[dname][''] = []
        thisage = now-s['time_create']
        if thisage > threshold:
          subscriptions[dname][''].append( common.Subscription(site=s['node'],age=thisage,group=s['group']) )
    #block-level
    if 'block' in d:
      for b in d['block']:
        bname = '#'+b['name'].split('#')[-1]
        if not (bname in subscriptions[dname]):
          subscriptions[dname][bname] = []
        for s in b['subscription']:
          thisage = now-s['time_create']
          if thisage > threshold:
            subscriptions[dname][bname].append( common.Subscription(site=s['node'],age=thisage,group=s['group']) )

  # now filter the stuck datasets
  emptyDatasets=set([])
  for dsname,ds in stuckDatasets.iteritems():
    # loop through each dataset
    try:
      datasetSub = subscriptions[dsname]
    except KeyError:
      emptyDatasets.add(dsname)
      continue

    emptyBlocks=set([])
    for blockname,block in ds.stuckBlocks.iteritems():
      # loop through each stuck block in the dataset

      toRemove = set([])
      for t in block.targets:
        # loop through all targets for that block

        if 'X' in t.node: # kill old disk
          toRemove.add(t)
          continue
        
        foundSub=False
        for blocknameSub,blockSub in datasetSub.iteritems():
          if foundSub:
            # already found what we want
            break
          if blocknameSub == '' or (dsname+blocknameSub == blockname):
            for sub in blockSub:
              if sub.node == t.node:
                # matched the correct subscription
                foundSub=True
                t.age = sub.age
                t.group = sub.group
                break
        if (not foundSub) or (t.age<threshold):
          toRemove.add(t)
          continue
        # done with target loop

      for t in toRemove:
        # remove all filtered targets for this block
        block.targets.remove(t)

      if len(block.targets)==0:
        #if no targets are remaining, block is empty
        emptyBlocks.add(blockname)

      #done with block loop

    for blockname in emptyBlocks:
      # remove empty blocks
      del ds.stuckBlocks[blockname]

    if len(ds.stuckBlocks)==0:
      # if no blocks, dataset is empty
      emptyDatasets.add(dsname)

    #done with dataset loop

  for dsname in emptyDatasets:
    #finally, remove empty datasets
    del stuckDatasets[dsname]

def addMissingFiles(stuck,bufferpath=''):
  if bufferpath=='':
    bufferpath = common.tmpdir + 'missingfiles.json'
  api = common.APIHandler('missingfiles')
  # api.VERBOSE=True
  for dsname,ds in stuck.iteritems():
    for blockname,block in ds.stuckBlocks.iteritems():
      flags = ' -O %s'%bufferpath
      for t in block.targets:
        params = {'node':t.node, 'block':block.name.replace('#','%23')} 
        api(params,flags)
        try:
          payload = common.getJson(bufferpath)['block'][0]['file'] # should only get one file back
          for f in payload:
            t.missingfiles.add(f['name'])
            t.volumemissing += f['bytes']
        except IndexError:
          print 'No missing files found!'
          pprint.pprint(common.getJson(bufferpath))


# def filterSubscriptions(stuckDatasets,bufferpath='',threshold=7):
#   if bufferpath=='':
#     bufferpath_sub = common.tmpdir+'subscription.json'
#     bufferpath_mis = common.tmpdir+'missingfiles.json'
#   api_sub = common.APIHandler(which='subscriptions',method='wget')
#   api_mis = common.APIHandler(which='missingfiles',method='wget')
#   now = time()
#   emptyDatasets=set([])
#   for dsname,ds in stuckDatasets.iteritems():
#     emptyBlocks=set([])
#     for blockname,block in ds.stuckBlocks.iteritems():
#       # first check when subscription was made
#       flags = ' -O %s'%bufferpath_sub
#       toRemove = set([])
#       for t in block.targets:
#         if 'X' in t.node:
#           toRemove.add(t)
#           continue
#         time_create = now
#         params = {'node':t.node, 'block':block.name.replace('#','%23')}
#         api_sub(params,flags)
#         payload = common.getJson(bufferpath_sub)
#         if not payload:
#           toRemove.add(t)
#           continue
#         payload = payload['dataset']
#         try:
#           time_create = int(payload[0]['block'][0]['subscription'][0]['time_create'])
#         except:
#           try:
#             time_create = int(payload[0]['subscription'][0]['time_create'])
#           except:
#             toRemove.add(t)
#             continue
#         if now-time_create < threshold*common.sPerDay:
#           toRemove.add(t)
#           continue
#       for t in toRemove:
#         block.targets.remove(t)
#       if len(block.targets)==0:
#         emptyBlocks.add(blockname)
#     for blockname in emptyBlocks:
#       del ds.stuckBlocks[blockname]
#     if len(ds.stuckBlocks)==0:
#       emptyDatasets.add(dsname)
#   for dsname in emptyDatasets:
#     del stuckDatasets[dsname]



