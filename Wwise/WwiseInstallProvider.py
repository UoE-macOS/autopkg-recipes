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


__all__ = ["WwiseInstallProvider"]


class WwiseInstallProvider(Processor):
    DOWNLOAD_DIR = 'wwise_downloads'
    REAL_INSTALL_PREFIX = "/"
    DEFAULT_VERSION = '2018.1.6_6858'

    """Provides an installation of Wwise, ready for packaging"""
    input_variables = {
        "wwise_version": {
            "required": False,
            "description": "Version. Defaults to %s" % DEFAULT_VERSION
        },
        "email": {
            "required": False,
            "description": "Email address to of Wwise account (optional)"
        },
        "password": {
            "required": False,
            "description": "Password of Wwise account (optional)"
        },
        "style": {
            "required": False,
            "description": "Mini or Maxi - defaults to mini"
        },
        "install_prefix": {
            "required": True,
            "description": "Path to installation"
        }
    }
    output_variables = {
        "install_root": {
            "description": "Location of the installed package root"
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
        sys.path.extend(self.env['RECIPE_SEARCH_DIRS'])
        import wwise_helper

        EMAIL = self.env.get('EMAIL', '')
        PASSWORD = self.env.get('PASSWORD', '')
        STYLE = self.env.get('INSTALL_STYLE', 'mini')

        # Build an argumeht list as if we were going to call our
        # helper tool on te commandline
        argv =  ['--bundle', self.env['VERSION'],
                 '--email', EMAIL,
                 '--password', PASSWORD,
                 '--install', STYLE,
                 '--download-dir', os.path.join(self.env['RECIPE_CACHE_DIR'], 
                                                self.DOWNLOAD_DIR),
                 '--install-prefix', self.env['install_prefix'],
                 '--real-install-prefix', '/' ]

        # Call our helper tool, passing it the argument list
        # we constructed above.
        wwise_helper.main(wwise_helper.process_args(argv))

if __name__ == "__main__":
    processor = WwiseInstallProvider()
    processor.execute_shell()
