#!/usr/bin/env python

import common
import json
import time

def makeBasicTable(stuckDatasets,templatefilepath,outfilepath):
  templatestring = '<tr data-hiddenval="HIDDEN"> <td class="details-control"></td>  <td> DATASETNAME </td> <td> BLOCKNAME </td> <td> NODENAME </td> <td> GROUP </td> <td id="center"> BLOCKMISSING </td> <td id="center"> DATASETMISSING </td> <td id="center"> BASIS </td> <td id="center"> AGE </td> <td> <a href="URL" target="_blank"> &#8599 </a></tr>\n'
  newrows = ''

  for dsname in sorted(stuckDatasets):
    ds = stuckDatasets[dsname]
    for blockname,block in ds.stuckBlocks.iteritems():
      blockname_ = '#' + blockname.split('#')[-1]
      for t in block.targets:
        newstring = templatestring
        newstring = newstring.replace('DATASETNAME',dsname)
        newstring = newstring.replace('BLOCKNAME',blockname_)
        newstring = newstring.replace('NODENAME',str(t.node))
        newstring = newstring.replace('BASIS',str(t.basis))
        newstring = newstring.replace('AGE','%.1f'%(t.age/common.sPerDay))
        newstring = newstring.replace('GROUP',t.group) 
        try:
          newstring = newstring.replace('BLOCKMISSING',"%.1f%%"%(100.*t.volumemissing/block.volume))
        except ZeroDivisionError:
          print "%s%s has block.volume=0?"%(dsname,blockname_)
          newstring = newstring.replace('BLOCKMISSING','100.0%')
        if t.node in ds.volumemissing:
          newstring = newstring.replace('DATASETMISSING',"%.3f%%"%(100.*ds.volumemissing[t.node]))
        else:
          newstring = newstring.replace('DATASETMISSING','-')

        missingurl = 'https://cmsweb.cern.ch/phedex/datasvc/perl/prod/missingfiles?&node=%s&block=%s'%(t.node,blockname.replace('#','%23'))
        newstring = newstring.replace('URL',missingurl)

        missingstring = ''
        for m in t.missingfiles:
          missingstring += '<br>%s'%m


        newstring = newstring.replace('HIDDEN',missingstring)
        newrows += newstring

  with open(templatefilepath) as templatefile:
    template = list(templatefile)

  with open(outfilepath,'w') as outfile:
    for line in template:
      outfile.write(line)
      if 'Insert newlines here' in line:
        outfile.write(newrows)
      if 'Last modified' in line:
        outfile.write(time.strftime('%Y-%m-%d\n',time.gmtime()))

def makeCSV(stuckDatasets,outfilepath):
  templatestring = 'DATASETNAME,BLOCKNAME,NODENAME,GROUP,BLOCKMISSING,DATASETMISSING,BASIS,AGE\n'
  newrows = templatestring

  for dsname in sorted(stuckDatasets):
    ds = stuckDatasets[dsname]
    for blockname,block in ds.stuckBlocks.iteritems():
      blockname_ = '#' + blockname.split('#')[-1]
      for t in block.targets:
        newstring = templatestring
        newstring = newstring.replace('DATASETNAME',dsname)
        newstring = newstring.replace('BLOCKNAME',blockname_)
        newstring = newstring.replace('NODENAME',str(t.node))
        newstring = newstring.replace('BASIS',str(t.basis))
        newstring = newstring.replace('AGE','%.1f'%(t.age/common.sPerDay))
        newstring = newstring.replace('GROUP',t.group) 
        try:
          newstring = newstring.replace('BLOCKMISSING',"%.1f%%"%(100.*t.volumemissing/block.volume))
        except ZeroDivisionError:
          print "%s%s has block.volume=0?"%(dsname,blockname_)
          newstring = newstring.replace('BLOCKMISSING','100.0%')
        if t.node in ds.volumemissing:
          newstring = newstring.replace('DATASETMISSING',"%.3f%%"%(100.*ds.volumemissing[t.node]))
        else:
          newstring = newstring.replace('DATASETMISSING','-')
        newrows += newstring

  with open(outfilepath,'w') as outfile:
    outfile.write(newrows)

def makeJson(stuckDatasets,outfilepath,basis):
  d = {}
  for dsname in sorted(stuckDatasets):
    ds = stuckDatasets[dsname]
    for blockname,block in ds.stuckBlocks.iteritems():
      blockname_ = '#' + blockname.split('#')[-1]
      for t in block.targets:
        if t.basis==basis:
          if dsname not in d:
            d[dsname] = {}
          if blockname_ not in d[dsname]:
            d[dsname][blockname_] = {}
          try:
            blockmissingfrac = t.volumemissing/block.volume
          except ZeroDivisionError:
            blockmissingfrac = 1
          d[dsname][blockname_][t.node] = {
            'AGE':t.age/common.sPerDay,
            'GROUP':t.group,
            'BLOCKMISSINGFRAC':blockmissingfrac,
          }
          if t.node in ds.volumemissing:
            d[dsname][blockname_][t.node]['DATASETMISSINGFRAC'] = ds.volumemissing[t.node]
  with open(outfilepath,'w') as outfile:
    json.dump(d,outfile,sort_keys=True,indent=4, separators=(',', ': '))
