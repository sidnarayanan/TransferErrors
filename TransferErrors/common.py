#!/usr/bin/env python

import os
import json
import urllib2
import logging

workdir = os.environ['TRANSFERERRORS']+'/'
webdir = os.environ['WEBDIR']+'/'
logging.basicConfig(level=10, format='%(asctime)-15s %(message)s')

siteNames = set([
     'T2_BE_IIHE','T2_ES_IFCA','T2_IT_Pisa','T2_RU_PNPI',
     'T2_US_Caltech','T2_BE_UCL','T2_FI_HIP','T2_IT_Rome',
     'T2_RU_RRC_KI','T2_US_Florida','T2_BR_SPRACE','T2_FR_CCIN2P3',
     'T2_KR_KNU','T2_RU_SINP','T2_US_MIT','T2_BR_UERJ',
     'T2_FR_GRIF_IRFU','T2_PK_NCP','T2_TH_CUNSTDA','T2_US_Nebraska',
     'T2_CH_CERN','T2_FR_GRIF_LLR','T2_PL_Swierk','T2_TR_METU',
     'T2_US_Purdue','T2_CH_CSCS','T2_FR_IPHC','T2_PL_Warsaw',
     'T2_TW_Taiwan','T2_US_UCSD','T2_CN_Beijing','T2_GR_Ioannina',
     'T2_PT_NCG_Lisbon','T2_UA_KIPT','T2_US_Wisconsin','T2_DE_DESY',
     'T2_HU_Budapest','T2_RU_IHEP','T2_UK_London_Brunel','T2_DE_RWTH',
     'T2_IN_TIFR','T2_RU_INR','T2_UK_London_IC','T2_EE_Estonia',
     'T2_IT_Bari','T2_RU_ITEP','T2_UK_SGrid_Bristol','T2_AT_Vienna',
     'T2_ES_CIEMAT','T2_IT_Legnaro','T2_RU_JINR','T2_UK_SGrid_RALPP',
     "T1_UK_RAL_Disk","T1_US_FNAL_Disk","T1_IT_CNAF_Disk","T1_DE_KIT_Disk",
     "T1_RU_JINR_Disk","T1_FR_CCIN2P3_Disk","T1_ES_PIC_Disk"
     ])

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

def getJson(jsonfile):
  try:
    payload = json.load(jsonfile)['phedex']
    return payload
  except Exception as e:
    print str(e)
    return None

class APIHandler():
  def __init__(self,which,cache=True):
    self.api = which
    self.VERBOSE=False
    self.url = None
  def __call__(self,params):
    self.url = 'http://cmsweb.cern.ch/phedex/datasvc/json/prod/%s?'%(self.api) # member variable so it can be checked after call
    for p in params:
      arg = params[p]
      param_str = '&%s=%s'%(p,str(arg))
      self.url += param_str
    logging.debug(self.url)
    payload = getJson(urllib2.urlopen(self.url))
    logging.debug('...retrieved')
    return payload

class Site():
  def __init__(self):
    self.bases = {}
    for iB in xrange(-6,3): 
      self.bases[iB]=0
    self.averageETA = 0
    self.counter = 0

class Subscription():
  def __init__(self,site,basis=0,age=0,group=None):
    self.node = site
    self.basis = basis
    self.age = age
    self.group = group
    self.missingfiles=set([])
    self.volumemissing=0
  def __str__(self):
    return 'Subscription(%20s %2i %2i %20s)'%(self.node,self.basis,int(self.age/sPerDay),self.group)

class TMDBDataset():
  def __init__(self,n):
    self.volume = 0
    self.name = n
    self.stuckBlocks = {}
    self.volumemissing = {} # doesn't have be to be filled for every Subscription if at block-level

class TMDBBlock():
  def __init__(self,n):
    self.volume = 0
    self.name = n
    self.targets = set([]) # set of Subscriptions

class TMDBFile():
  def __init__(self,n):
    self.name = n
    self.missing = {}
    self.complete = []

