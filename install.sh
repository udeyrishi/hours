#!/bin/bash

SCRIPTPATH="$(cd "$(dirname "$0")" && pwd -P)"
MAIN_FILE=${SCRIPTPATH%%/}/hour_logger.py
chmod a+x $MAIN_FILE
ln -s $MAIN_FILE /usr/local/bin/hours
chmod a+x /usr/local/bin/hours