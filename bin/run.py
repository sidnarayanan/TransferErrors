#!/usr/bin/env python

import TransferErrors as TE
import cPickle as pickle
import argparse
from sys import argv

parser = argparse.ArgumentParser()
parser.add_argument('--refresh',action='store_true')

refresh = parser.parse_args(argv[1:]).refresh

print 'Getting block arrive'
TE.getBlockArrive(skip=[0,-2],refresh=refresh)

print 'Getting subscriptions'
TE.getSubscriptions(refresh=refresh,window=90)
# TE.getErrorLogs()

print 'Parsing block arrive'
stuck=TE.parseBlockArrive(threshold=5)

print 'Filtering subscriptions'
TE.filterSubscriptions(stuck,threshold=5)

print 'Adding missing file info'
TE.addMissingFiles(stuck)

print 'Dumping'
with open('stuck.pkl','wb') as pklfile:
  pickle.dump(stuck,pklfile)

'''
for k,v in stuck.iteritems():
  print k
  for bn,b in v.stuckBlocks.iteritems():
    print '\t',bn 
    for t in b.targets:
      print '\t\t',t
'''
