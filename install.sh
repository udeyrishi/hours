#!/bin/bash

if [ -z "$1" ]
    then
        NAME=hours
    else
        NAME=$1
fi

SCRIPTPATH="$(cd "$(dirname "$0")" && pwd -P)"
MAIN_FILE=${SCRIPTPATH%%/}/hour_logger.py
chmod a+x $MAIN_FILE
ln -s $MAIN_FILE /usr/local/bin/$NAME
chmod a+x /usr/local/bin/$NAME