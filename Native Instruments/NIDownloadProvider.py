#!/usr/bin/env python
#
# Copyright 2018 The University of Edinburgh, by Geoff Lee
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys
from autopkglib import Processor, ProcessorError


__all__ = ["NIDownloadProvider"]


class NIDownloadProvider(Processor):
    """Provides an installation of Wwise, ready for packaging"""
    input_variables = {
        "version": {
            "required": False,
            "description": "Version. Only '11' is currently supported"
        },
        "product": {
            "required": False,
            "description": "Product: only 'Komplete' is currently supported"
        },
        "downloads": {
            "required": True,
            "description": "Where to download packages to"
        }
    }
    output_variables = {
        "version": {
            "description": "The version that was installed"
        },
    }
    description = __doc__

    def main(self):
        """ Install the requested version of Wwise to the requested
            directory
        """
        # Hack alert - add RECIPE_SEARCH_DIRS to sys.path
        # so that we can load our wwise_helper. I suspect this
        # is not very AutoPkgythonic.
        sys.path.append(os.path.dirname(self.env['RECIPE_PATH']))
	    
        import native_instruments_helper

        # Build an argumeht list as if we were going to call our
        # helper tool on the commandline
        argv =  ['--packages', '--download-dir', self.env['downloads']]

        # Call our helper tool, passing it the argument list
        # we constructed above.
        native_instruments_helper.main(native_instruments_helper.process_args(argv))

if __name__ == "__main__":
    processor = NIDownloadProvider()
    processor.execute_shell()
