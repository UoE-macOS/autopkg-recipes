#!/usr/bin/env python
#
# Copyright 2020 Geoff Lee
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
import subprocess

__all__ = ["CredentialsProvider"]


class CredentialsProvider(Processor):

    """This processor takes input of a file, and a value to look up
       if the file is a keychain, the creds will be looked up in it.
       If no file is specified, the login keychain of the current user is used.
    """

    input_variables = {
        "source": {
            "required": False,
            "description": "Keychain file to operate on",
        },
        "server": {
            "required": True,
            "description": "Name of the server to match ",
        },
        "account": {
            "required": True,
            "description": "Name of the account to match "
        },
        "attributes": {
            "required": False,
            "description": 'A list of attributes to be returned. Does nothing yet.'
        }
    }

    # Will match the attributes requested... if that turns out to be possible.
    output_variables = { 
         "password": {
            "description": "The password for the requested account"
        },
    }

    description = __doc__

    def main(self):
        """ Where the magic happens... """
        source = self.env.get("source", None)
        server = self.env["server"]
        account = self.env["account"]

        # Use login keychain by default
        if source is None:
            source = self._get_login_keychain()

        if source.endswith('.keychain-db'):
            password = self._lookup_keychain(source, server, account)
            self.env['password'] = password
        else:
            raise ProcessorError("Unsupported source file. Only keychain supported just now")
        


    def _get_login_keychain(self):
        command = ['/usr/bin/security', 'login-keychain']
        result = subprocess.check_output(command)
        return result.strip()[1:-1]


    def _lookup_keychain(self, keychain, server, account):
        """ Shell out to the security command """
        command = ["/usr/bin/security", "find-internet-password",
                   "-w", "-s", server, "-a", account, keychain]

        try:
            password = subprocess.check_output(command)
        except subprocess.CalledProcessError as err:
            raise ProcessorError("Failed to get password for {}".format(server), err)

        return password.strip()
         
if __name__ == "__main__":
    processor = CredentialsProvider()
    processor.execute_shell()
