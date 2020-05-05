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
            "description": "Version. Currently does nothing. You get the latest version."
        },
        "product_uuid": {
            "required": True,
            "description": "UUID of the product you want to package"
        },
        "downloads": {
            "required": True,
            "description": "Where to download packages to"
        },
        "output": {
            "required": True,
            "description": "'package' or 'download'"
        },
        "username": {
            "required": True,
            "description": "Username for Native Instruments account"
        },
        "password": {
            "required": True,
            "description": "Password for Native Instruments account"
        }
    }
    output_variables = {
        "version": {
            "description": "The version of the product that was produced"
        },
        "package_path": {
            "description": "The path to the package (if any) that was produced"
        },
        "download_path": {
            "description": "The path to the item (if any) that was downloaded"
        },
        "ni_downloader_summary_result": {
            "description": "Description of interesting results."
        }
    }
    description = __doc__

    def main(self):
        """ Do stuff.
        """
        # Hack alert - add RECIPE_SEARCH_DIRS to sys.path
        # so that we can load our wwise_helper. I suspect this
        # is not very AutoPkgythonic.
        sys.path.append(os.path.dirname(self.env['RECIPE_PATH']))

        # Even more of a hack so that this works for overridden recipes
        for path in self.env['PARENT_RECIPES']:
            sys.path.append(os.path.dirname(path))
	    
        if self.env['downloads'] == '':
            self.env['downloads'] = os.path.join(self.env['RECIPE_CACHE_DIR'], 'ni_downloads')

        import native_instruments_helper


        print(self.env['output'])
        # Build an argument list as if we were going to call our
        # helper tool on the commandline
        argv =  ['--download-dir', self.env['downloads'],
                 '--product-uuid', self.env['product_uuid'],
                 '--username', self.env['username'],
                 '--password', self.env['password'] ]

        output = self.env['output']
        if output == "package":
            argv.append('--packages')
            report_field = 'package_path'
        elif output == "download":
            argv.append('--download-only')
            report_field = 'download_path'
        else:
            raise EnvironmentError("Unknown output mode: %s".format(output))

        # Call our helper tool, passing it the argument list
        # we constructed above.
        report_data = native_instruments_helper.main(native_instruments_helper.process_args(argv))

        if report_data:
            self.env["ni_downloader_summary_result"] = {
                'summary_text': ("The NIDownloader processor created the following items:\n"),
                'report_fields': [report_field, 'version'],
                 # The helper tool is capable of creating multiple packages in a single 
                 # invocation; however, autopkg can only report on one, and we only ever
                 # ask it to create a single package.
                 # This needs to be a dict.
                'data': report_data[0]
            }

            # Set our other output variables
            self.env['version'] = report_data[0]['version']
            self.env[report_field] = report_data[0][report_field]

if __name__ == "__main__":
    processor = NIDownloadProvider()
    processor.execute_shell()
