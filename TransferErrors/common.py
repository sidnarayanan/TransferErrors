#!/usr/bin/env python

tmpdir = '/tmp/'

basis = {
 -6 : 'at least one file has no source replica remaining',
 -5 : 'no path from source to destination',
 -4 : 'automatically suspended by router for too many failures',
 -3 : 'no active download link to the destination',
 -2 : 'manually suspended',
 -1 : 'block is still open',
  0 : 'all files in the block are currently routed',
  1 : 'not yet routed because the destination queue is full',
  2 : 'at least one file is waiting for rerouting',
}

sPerDay=86400

class Site():
  def __init__(self):
    self.bases = {}
    for iB in xrange(-6,3): 
      self.bases[iB]=0
    self.averageETA = 0
    self.counter = 0

class TMDBDataset():
  def __init__(self,n):
    self.name = n
    self.blocks = {}
  def __str__(self):
    sites = {}
    for block,obj in self.blocks.iteritems():
      sb = obj.getStatus()
      for site in sb:
        if site not in sites:
          sites[site] = Site()
        for iB in xrange(-6,3):
          sites[site].bases[iB] += sb[site].bases[iB]
        sites[site].counter += sb[site].counter
        if sites[site].averageETA!=None and sb[site].averageETA!=None:
          sites[site].averageETA += sb[site].averageETA*sb[site].counter
        else:
          sites[site].averageETA=None
    for site in sites:
      if sites[site].averageETA!=None:
        sites[site].averageETA /= sites[site].counter
    s = self.name + ' is waiting on %i sites\n'%len(sites)
    for sitename,site in sites.iteritems():
      s += '\t' + sitename + ': '
      if site.averageETA!=None:
        s += 'ETA=%.3g days\n'%((site.averageETA-time())/86400.)
      else:
        s += 'ETA=unknown\n'
      for iB in xrange(-6,3):
        if site.bases[iB]>0:
          s += '\t\t%4i stuck in %2i (%s)\n'%(site.bases[iB],iB,basis[iB])
    return s

class TMDBBlock():
  def __init__(self,n):
    self.name = n
    self.files = {}
  def getStatus(self):
    sites = {}
    for lfn,obj in self.files.iteritems():
      for site,info in obj.missing.iteritems():
        if site not in sites:
          sites[site] = Site()
        sites[site].bases[info[0]] += 1
        sites[site].counter += 1
        if sites[site].averageETA!=None and type(info[1])==type(1.):
          sites[site].averageETA += info[1]
        else:
          sites[site].averageETA = None
    for site in sites:
      if sites[site].averageETA!=None:
        sites[site].averageETA /= sites[site].counter
    return sites

class TMDBFile():
  def __init__(self,n):
    self.name = n
    self.missing = {}
    self.complete = []
