#!/usr/bin/env python

import TransferErrors as TE
import cPickle as pickle

print 'Getting block arrive'
TE.getBlockArrive(skip=[0,-2])

print 'Getting subscriptions'
TE.getSubscriptions()
# TE.getErrorLogs()

print 'Parsing block arrive'
stuck=TE.parseBlockArrive(threshold=7)

print 'Filtering subscriptions'
TE.filterSubscriptions(stuck)

print 'Adding missing file info'
TE.addMissingFiles(stuck)

with open('stuck.pkl','wb') as pklfile:
  pickle.dump(stuck,pklfile)

for k,v in stuck.iteritems():
  print k
  for bn,b in v.stuckBlocks.iteritems():
    print '\t',bn 
    for t in b.targets:
      print '\t\t',t