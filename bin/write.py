#!/usr/bin/env python

import TransferErrors as TE
import cPickle as pickle

with open('stuck.pkl','rb') as pklfile:
  stuck = pickle.load(pklfile)

TE.makeBasicTable(stuck,TE.workdir+'html/table.html',TE.webdir+'table.html')
TE.makeCSV(stuck,TE.webdir+'data.csv')

for basis in [-6,-5,-4,-3,-1,1,2]:
  TE.makeJson(stuck,TE.webdir+('stuck_%i'%basis).replace('-','m')+'.json',basis)
