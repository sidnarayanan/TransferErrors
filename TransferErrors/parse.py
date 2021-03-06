#!/usr/bin/env python

import common
import json
from time import time
import pprint
import os 

ba_api = common.APIHandler('blockarrive')
el_api = common.APIHandler('errorlog')
subs_api= common.APIHandler('subscriptions')
mf_api = common.APIHandler('missingfiles')


def parseBlockArrive(skip=[0,-2],threshold=0):
  stuckDatasets = {}
  now = time()

  for iB in xrange(-6,3):
    if iB in skip:
      continue
    payload = ba_api({'basis':iB})
    if not payload:
      continue
    for block in payload['block']:
      blockname = block['name']
      datasetname = block['dataset']
      time_create = block['time_create']
      if now-time_create < threshold*common.sPerDay:
        continue 
      try:
        dataset = stuckDatasets[datasetname]
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
        if not('T3' in dest['name']):
          stuckBlock.targets.add(common.Subscription(dest['name'],iB))
  return stuckDatasets 

def filterSubscriptions(stuckDatasets,threshold=7):
  now = time()
  threshold *= common.sPerDay

  # parse the subscriptions
  params = {'create_since' :  now - 60*common.sPerDay,
            'block' : os.getenv('DATASETPATTERN') + '%23*',
            'collapse' : 'n',
            'suspended' : 'n',
            'percent_max' : 99.999}
  payload = subs_api(params)['dataset']
  subscriptions = {} # dataset : {block:[common.Subscription]}
  volumemissing = {} # dataset : {site:vol} - only filled for dataset-level subscriptions
  volume        = {} # dataset : volume
  for d in payload:
    dname = d['name']
    vol = 1.*d['bytes']
    volume[dname] = vol
    if not (dname in subscriptions):
      subscriptions[dname] = {}
      volumemissing[dname] = {}
    # dataset-level
    # pprint.pprint(d)
    if 'subscription' in d:
      for s in d['subscription']:
        if not('' in subscriptions[dname]):
          subscriptions[dname][''] = []
        thisage = now-s['time_create']
        if thisage > threshold:
          subscriptions[dname][''].append( common.Subscription(site=s['node'],age=thisage,group=s['group']) )
          try:
            volumemissing[dname][s['node']] = 1. - s['node_bytes']/vol
          except TypeError:
            volumemissing[dname][s['node']] = 1.

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

    ds.volumemissing = volumemissing[dsname]
    ds.volume = volume[dsname]

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

DOMISSINGFILES=False

def addMissingFiles(stuck,bufferpath=''):
  counter=0
  for dsname,ds in stuck.iteritems():
    flags = ' -O %s'%bufferpath
    params = {'block':dsname+'%23*'} 
    if DOMISSINGFILES:
      payload = mf_api(params)
    volumemissing = {} # site : vol
    for blockname,block in ds.stuckBlocks.iteritems():
      thispayload = None
      if DOMISSINGFILES:
        for pb in payload:
          if pb['name']==blockname:
            thispayload=pb
            break
      for t in block.targets:
        if t.node not in volumemissing:
          volumemissing[t.node] = 0
        if not DOMISSINGFILES:
          volumemissing[t.node] += block.volume # assume the whole block is missing
          continue
        counter+=1
        if thispayload:
          for f in thispayload['file']:
            for m in f['missing']:
              if m['node_name']==t.node:
                t.missingfiles.add(f['name'])
                t.volumemissing += f['bytes']
                volumemissing[t.node] += f['bytes']
        else:
          print '######################################'
          print 'No missing files found for block with basis=%i!'%t.basis,counter
          print missingfiles.url
          pprint.pprint(payload)
          pprint.pprint(params)
          print '######################################'
    for n,v in volumemissing.iteritems():
      try:
        ds.volumemissing[n] = 1.*v/ds.volume
      except ZeroDivisionError:
        print 'dataset=%s has volume=0?'%(dsname)
        ds.volumemissing[n] = 0.



