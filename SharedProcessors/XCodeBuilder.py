#!/usr/bin/env python
#
# Copyright 2019 The University of Edinburgh, by Geoff Lee
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
import subprocess
from autopkglib import Processor, ProcessorError


__all__ = ["XCodeBuilder"]


class XCodeBuilder(Processor):
    """Attempts to build the specified xcode project file"""
    input_variables = {
        "project_file": {
            "required": True,
            "description": "Path to the .xcodeproj file that you want to build"
        },
        "target": {
            "required": False,
            "description": "A specific target to build. Defaults to the default target",
            "default": None
        },
        "build_config": {
            "required": False,
            "description": "A specific build configuration to use. Defaults to 'Debug'",
            "default": "Debug"
        }
    }
    output_variables = {
        "product_path": {
            "description": "Path to the product produced by the `xcodebuild` command"
        },
        "product_name": {
            "description": "Name of the product produced by the `xcodebuild` command"
        },
        "xcode_builder_summary_result": {
            "description": "Description of interesting results."
        }
    }
    description = __doc__


    def __init__(self, env=None, infile=None, outfile=None):   
        super(XCodeBuilder, self).__init__(env, infile, outfile)

        self.build_cmd = None
        self.build_settings_cmd = None

        self.build_settings = {}
        self.something_was_built = False

    def _get_build_setting(self, var_name):
        """ Return the value of a build variable """
        # Find the build setting that matches `var_name`
        try: 
            return self.build_settings[var_name]
        except KeyError:
            raise ProcessorError("Couldn't find a build setting called {}".format(var_name))

    def _init_build_settings(self):
        """ Pull all of our build settings into a dict
            so that we can look them up as needed """
        # This should yeild a list of 'x = y' strings
        output = [l for l in subprocess.check_output(self.build_settings_cmd).split("\n")]
        # Naively parse and add to a dict - will break if any variable
        # names contain '=' characters!
        for line in output:
            self.build_settings[line.split('=')[0].strip()] = line.split('=')[-1].lstrip()

    def main(self):
        """ Do stuff.
        """
        self.build_cmd = ["/usr/bin/xcodebuild", 
                          "-project", self.env["project_file"],
                          "-configuration", self.env["build_config"]]
        
        if self.env["target"]:
            self.build_cmd.append["-target", self.env["target"]]

        self.build_settings_cmd = self.build_cmd + ["-showBuildSettings"]

        if not os.path.isdir(self.env["project_file"]):
            raise ProcessorError("{} doesn't seem to be a project!".format(self.env["project_file"]))

        self._init_build_settings()

        # Query the xcode project build settings to work out 
        # what we are building and where it will end up
        products_dir = self._get_build_setting('BUILT_PRODUCTS_DIR')
        product_name = self._get_build_setting('FULL_PRODUCT_NAME')
 
        self.output("Project File: {}".format(self.env["project_file"]))
        self.output("Products Dir: {}".format(products_dir))
        self.output("Product Name: {}".format(product_name))

        self.output("Looking for existing product at {}".format(os.path.join(products_dir, product_name)))

        # Don't build if our expected product already exists
        if os.path.exists(os.path.join(products_dir, product_name)):
            self.output("{} exists. Skipping build.".format(os.path.join(products_dir, product_name)))
        else:
            # Perform the build
            try:
                subprocess.check_call(self.build_cmd)
            except subprocess.CalledProcessError as e:
                raise ProcessorError("Failed to build: {}".format(e))

            self.something_was_built = True

        if self.something_was_built:
            self.env["xcode_builder_summary_result"] = {
                'summary_text': "The following items were built:\n",
                'report_fields': ['product', 'path'],
                'data': {'product': product_name, 'path': os.path.join(products_dir, product_name)}
            }

        # Set our output variables
        self.env['product_path'] = os.path.join(products_dir, product_name)
        self.env['product_name'] = product_name
        
if __name__ == "__main__":
    processor = XCodeBuilder()
    processor.execute_shell()
