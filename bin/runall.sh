#!/bin/bash

cd /home/snarayan/public_html/TransferErrors/
source ./setup.sh
cd bin
python run.py # --refresh
python write.py
