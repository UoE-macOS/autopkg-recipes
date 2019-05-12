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
        }
    }
    output_variables = {
        "version": {
            "description": "The version that was installed"
        },
        "ni_downloader_summary_result": {
            "description": "Description of interesting results."
        }
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
	    
        if self.env['downloads'] == '':
            self.env['downloads'] = os.path.join(self.env['RECIPE_CACHE_DIR'], 'ni_downloads')

        print("Download path: ", self.env['downloads'])
        import native_instruments_helper

        # Build an argument list as if we were going to call our
        # helper tool on the commandline
        argv =  ['--packages', '--download-dir', self.env['downloads'],
                 '--product-uuid', self.env['product_uuid'] ]

        # Call our helper tool, passing it the argument list
        # we constructed above.
        report_data = native_instruments_helper.main(native_instruments_helper.process_args(argv))

        if report_data:
            self.env["ni_downloader_summary_result"] = {
                'summary_text': ("NIDownloader processor ran successfully. "
                                 "the following items were created:\n"),
                'report_fields': ['package', 'version'],
                'data': report_data
            }

if __name__ == "__main__":
    processor = NIDownloadProvider()
    processor.execute_shell()
