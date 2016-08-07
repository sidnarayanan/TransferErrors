#!/usr/bin/env python

import common
from time import time

def getBlockArrive(refresh=False,bufferpath=''):
  if bufferpath=='':
    bufferpath = common.tmpdir+'blockarrive.json'
  if not refresh:
    

