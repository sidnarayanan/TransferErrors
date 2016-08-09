#!/usr/bin/env python

import TransferErrors as TE
import cPickle as pickle

with open('stuck.pkl','rb') as pklfile:
  stuck = pickle.load(pklfile)

TE.makeBasicTable(stuck,TE.workdir+'html/table.html',TE.workdir+'www/table.html')