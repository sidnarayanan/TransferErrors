#!/usr/bin/env python

import TransferErrors as TE

stuck=TE.parseBlockArrive()
TE.filterSubscriptions(stuck)
for k,v in stuck.iteritems():
  print k
  for bn,b in stuck.stuckBlocks.iteritems():
    print b.targets