#!/usr/bin/env python

import TransferErrors as TE
import cPickle as pickle

TE.getBlockArrive()
TE.getSubscriptions()
# TE.getErrorLogs()

stuck=TE.parseBlockArrive(threshold=7)
TE.filterSubscriptions(stuck)

with open('stuck.pkl','wb') as pklfile:
  pickle.dump(stuck,pklfile)

for k,v in stuck.iteritems():
  print k
  for bn,b in v.stuckBlocks.iteritems():
    print '\t',bn 
    for t in b.targets:
      print '\t\t',t