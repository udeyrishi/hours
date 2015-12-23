#!/usr/local/bin/python3

"""
Copyright 2015 Udey Rishi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import modes


def main():
    debug = False

    args = sys.argv

    if '--debug' in args:
        debug = True
        args.remove('--debug')

    try:
        mode = modes.get_mode(args[1:])
        mode.run()

    except Exception as e:
        if debug:
            raise e
        else:
            print('Error:', e)


if __name__ == '__main__':
    main()
