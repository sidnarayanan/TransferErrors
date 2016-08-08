#!/usr/bin/env python

import os
import json

tmpdir = '/tmp/'

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

def getJson(fpath):
  try:
    with open(fpath) as jsonfile:
      payload = json.load(jsonfile)['phedex']
    return payload
  except IOError:
    return None

class APIHandler():
  def __init__(self,which,method='wget'):
    self.api = which
    self.method = method
    self.VERBOSE=False
  def __call__(self,params,flags=''):
    if self.method=='wget':
      return self.callWget(params,flags)
    else:
      print 'ERROR [TransferErrors.APIHandler]: Method %s is not supported yet'%(self.method)
      return
  def callWget(self,params,flags=''):
    flags = ' --no-check-certificate '+flags
    url = '"https://cmsweb.cern.ch/phedex/datasvc/json/prod/%s?'%(self.api)
    for p in params:
      arg = params[p]
      param_str = '&%s=%s'%(p,str(arg))
      url += param_str
    url += '"'
    outputflag = '' if self.VERBOSE else ' > /dev/null'
    cmd = 'wget %s %s %s'%(flags,url,outputflag)
    if self.VERBOSE: print cmd
    os.system(cmd)

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
    self.stuckBlocks = {}

class TMDBBlock():
  def __init__(self,n):
    self.name = n
    self.targets = set([]) # tuples ('TX_XXX_XXX',basis)
    self.files = {}

class TMDBFile():
  def __init__(self,n):
    self.name = n
    self.missing = {}
    self.complete = []
