#!/usr/bin/env python

import common

def makeBasicTable(stuckDatasets,templatefilepath,outfilepath):
  templatestring = '<tr>  <td> DATASETNAME </td> <td> BLOCKNAME </td> <td> NODENAME </td> <td id="center"> BASIS </td> <td id="center"> AGE </td> <td> <a href="URL" target="_blank"> &#8599 </a></tr>\n'
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
        newstring = newstring.replace('URL','https://cmsweb.cern.ch/phedex/datasvc/perl/prod/missingfiles?&node=%s&block=%s'%(t.node,blockname.replace('#','%23')))
        newrows += newstring

  with open(templatefilepath) as templatefile:
    template = list(templatefile)

  with open(outfilepath,'w') as outfile:
    for line in template:
      outfile.write(line)
      if 'Insert newlines here' in line:
        outfile.write(newrows)

