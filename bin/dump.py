#!/usr/bin/env python

import cPickle as pickle
import TransferErrors as TE
import ROOT as root
from tdrStyle import *

setTDRStyle()

with open('stuck.pkl','rb') as pklfile:
  stuck = pickle.load(pklfile)

basisMap = {
  -6 : 3,
  -5 : 2, 
  -4 : 5,
  -3 : 7,
  -1 : 4,
   1 : 1,
   2 : 6,
}
revMap = {v:k for k,v in basisMap.iteritems()}

hAge = root.TH1F('hAge','',10,7,60); hAge.GetXaxis().SetTitle('Days'); hAge.GetYaxis().SetTitle('Blocks'); hAge.SetStats(0); hAge.SetMinimum(0)
hBasis = root.TH1F('hBasis','',7,0.5,7.5); hBasis.GetXaxis().SetTitle(''); hBasis.GetYaxis().SetTitle('Blocks'); hBasis.SetStats(0); hBasis.SetMinimum(0)
xaxis = hBasis.GetXaxis()
xaxis.SetBinLabel(basisMap[-6],'Missing file')
xaxis.SetBinLabel(basisMap[-5],'Missing link')
xaxis.SetBinLabel(basisMap[-4],'Too many failures')
xaxis.SetBinLabel(basisMap[-3],'No DL link')
xaxis.SetBinLabel(basisMap[-1],'Open block')
xaxis.SetBinLabel(basisMap[1],'Full queue')
xaxis.SetBinLabel(basisMap[2],'Rerouting')

csv = []

templatestring = 'DATASETNAME BLOCKNAME NODENAME BASIS AGE GROUP BLOCKMISSING DATASETMISSING\n'
csv.append(templatestring)

for dsname in sorted(stuck):
  ds = stuck[dsname]
  for blockname,block in ds.stuckBlocks.iteritems():
    blockname_ = '#' + blockname.split('#')[-1]
    for t in block.targets:
      hAge.Fill(t.age/TE.sPerDay,1)
      hBasis.Fill(basisMap[t.basis],1)
      newstring = templatestring
      newstring = newstring.replace('DATASETNAME',dsname)
      newstring = newstring.replace('BLOCKNAME',blockname_)
      newstring = newstring.replace('NODENAME',str(t.node))
      newstring = newstring.replace('BASIS',str(t.basis))
      newstring = newstring.replace('AGE','%.1f'%(t.age/TE.sPerDay))
      newstring = newstring.replace('GROUP',t.group) 
      newstring = newstring.replace('BLOCKMISSING',"%f"%(t.volumemissing/block.volume))
      if t.node in ds.volumemissing:
        newstring = newstring.replace('DATASETMISSING',"%f"%(ds.volumemissing[t.node]))
      else:
        newstring = newstring.replace('DATASETMISSING','-')
      csv.append(newstring)

c = root.TCanvas('c','c',1200,1000)
hAge.SetLineColor(2); hAge.SetLineWidth(3); hAge.Draw('hist')
c.SaveAs('age.png')
c.SaveAs('age.pdf')

c.Clear()
c.SetBottomMargin(0.15)
hBasis.SetLineColor(1); hBasis.SetFillColor(root.kCyan); hBasis.SetFillStyle(1001); hBasis.Draw('hist')
c.SaveAs('basis.png')
c.SaveAs('basis.pdf')


with open('stuck.csv','w') as csvfile:
  for l in csv:
    csvfile.write(l)