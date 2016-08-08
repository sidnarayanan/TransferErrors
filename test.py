#!/usr/bin/env python

import TransferErrors as TE
import cPickle as pickle



TE.getBlockArrive()
TE.getErrorLogs()

stuck=TE.parseBlockArrive()
TE.filterSubscriptions(stuck)

with open('stuck.pkl','wb') as pklfile:
  pickle.dump(stuck,pklfile)

# print stuck
for k,v in stuck.iteritems():
  print k
  for bn,b in v.stuckBlocks.iteritems():
    print '\t',b.targets