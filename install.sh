#!/bin/bash

# Copyright 2015 Udey Rishi

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if [ -z "$1" ]
    then
        NAME=hours
    else
        NAME=$1
fi

SCRIPTPATH="$(cd "$(dirname "$0")" && pwd -P)"
MAIN_FILE=${SCRIPTPATH%%/}/hour_logger.py
LINK_FILE=/usr/local/bin/$NAME

# Soft link the script in /usr/local/bin
chmod a+x $MAIN_FILE
ln -s $MAIN_FILE $LINK_FILE
chmod a+x $LINK_FILE

# Generate the BitBar plugin file in the script location dir
PLUGIN_PATH=${SCRIPTPATH%%/}/${NAME}.1h.sh
echo "#!/bin/bash" > $PLUGIN_PATH
echo ${LINK_FILE}" --bitbar" >> $PLUGIN_PATH
chmod a+x $PLUGIN_PATH
