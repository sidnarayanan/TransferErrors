#!/bin/bash

export PYTHONPATH=${PYTHONPATH}:${PWD}
export TRANSFERERRORS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export WEBDIR=${TRANSFERERRORS}/www/
export DATASETPATTERN='/*/*/*' # this is the default value for prod. can be used for testing
