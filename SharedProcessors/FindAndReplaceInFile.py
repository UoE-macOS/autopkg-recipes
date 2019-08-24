#!/usr/bin/env python
#
# Copyright 2016 Elliot Jordan, Geoff Lee
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

from autopkglib import Processor, ProcessorError  # noqa: F401

__all__ = ["FindAndReplaceInFile"]


class FindAndReplaceInFile(Processor):

    """This processor does one thing only: It searches the file you
    specify and replaces instances of the "find" string with the "replace"
    string.
    """

    input_variables = {
        "file": {
            "required": True,
            "description": "The file you want to perform find/replace on.",
        },
        "find": {
            "required": True,
            "description": "This string, if found, will be replaced with the "
            '"replace" string.',
        },
        "replace": {
            "required": True,
            "description": 'The string that you want to replace the "find" '
            "string with.",
        },
         "count": {
            "required": False,
            "description": "Number of occurrences of the string you woud like to replace "
            " - defaults to all occurrences",
        },
    }

    output_variables = {}

    description = __doc__

    def main(self):
        """ Where the magic happens... """
        the_file = self.env["file"]
        find = self.env["find"]
        replace = self.env["replace"]
        count = self.env.get("count", 'ALL')

        replace_args = (find, replace)

        if not count == 'ALL':
            replace_args = replace_args + (count,)

        with open(the_file, 'r') as fh:
            self.output('Replacing "%s" with "%s" in "%s", %s times.' % (find, 
                                                                        replace, 
                                                                        the_file, 
                                                                        count))
            content = fh.read()

        with open(the_file, 'w') as fh:
            self.output(content, 2)
            fh.write(content.replace(*replace_args))

if __name__ == "__main__":
    processor = FindAndReplace()
    processor.execute_shell()
