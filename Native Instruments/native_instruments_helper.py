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
from __future__ import print_function
import urllib2
import sys
import os
import json
import shutil
import subprocess
import argparse
import tempfile
import time
import plistlib
from functools import wraps
from socket import error as SocketError
from distutils.version import LooseVersion
import xml.etree.ElementTree as ET


VERSION = '0.0.1'
DESCRIPTION = 'TBD'

def process_args(argv=None):
    """Process any commandline arguments"""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     version=VERSION)

    parser.add_argument('--download-dir',
                        dest='DOWNLOAD_DIR', default='./_downloads', 
                        help=('Directory in which to download the installers.'
                              'Installers will be deleted when finished, unless '
                              '--preserve-downloads is specified '
                              'Default: ./_downloads'))

    parser.add_argument('--suite',
                        dest='SUITE', default=None, 
                        help=('Suite to package. There must be a corresponding file in the '
                              'product_lists directory in the same directory as this script'))

    parser.add_argument('--major-version',
                        dest='MAJOR_VERSION', default=None, 
                        help=('Major version of SUITE to package. There must be a corresponding ' 
                              'file in the product_lists directory in the same directory as this script'))

    parser.add_argument('--preserve-downloads', default=False, action='store_true',
                        dest='PRESERVE', help=('Do not delete downloads after installation. '
                                               'WARNING: requires at least 130GB of free space ' 
                                               'in the download directory, PLUS the same again on '
                                               'the installation target.'))

    parser.add_argument('--download-only', default=False, action='store_true',
                        dest='DOWNLOAD_ONLY', 
                        help=('Do not install, only download (implies --preserve-downloads)'))

    parser.add_argument('--updates-only', default=False, action='store_true',
                        dest='UPDATES_ONLY', 
                        help=('Do not look for new full product installers, only updates. This '
                              'can hopefully be used to update an existing installation. YMMV'))
    
    parser.add_argument('--updates', default=False, action='store_true',
                        dest='UPDATES', 
                        help=('Look for updates as well as full products. Generally, full products '
                              'are already the latest version, so you probably want --updates-only '
                              'instead of this option if you are looking for updates.'))

    parser.add_argument('--packages', default=False, action='store_true',
                        dest='PACKAGES', 
                        help=('Copy packages into a subfolder in the downloads folder.'
                              'implies --download-only'))

    parser.add_argument('--product-uuid', dest='UUID', 
                        help=('Give the UUID of a single product to operate on it '
                              'individually'))

    parser.add_argument('--template-autopkg-override', dest='AUTOPKG_OVERRIDE', action='store_true',
                        help=('Template an autopkg override file using OVERRIDE_SOURCE and writing the  '
                              'output to OVERRIDE_DEST'))

    parser.add_argument('--template-override-source', dest='OVERRIDE_SOURCE',
                        help=('Source file to use for templating override files  '

                              ''))
    parser.add_argument('--template-override-dest-dir', dest='OVERRIDE_DEST',
                        help=('Destination directory for templating override files  '
                              ''))

    args = parser.parse_args(argv)

    if args.DOWNLOAD_ONLY:
        args.PRESERVE = True

    return args

INSTALL_RECEIPTS = '/var/db/NativeInstrumentsReceipts.txt'

BASEURL = 'https://api.native-instruments.com/'

NATIVE_ACCESS_URL = 'https://www.native-instruments.com/fileadmin/downloads/Native_Access_Installer.dmg'

PROTOBUF_HEADERS = {'Accept': 'application/x-protobuf',
                    'Content-Type': 'application/x-protobuf'}

JSON_HEADERS = {'Accept': 'application/json',
                'Content-Type': 'application/x-protobuf'}

METALINK_HEADERS = {'Accept': 'application/metalink4+xml'}

USER_AGENT = {'User-Agent': 'NativeAccess/1.7.2 (R88)'}

AUTH_HEADER = {'Authorization': ''}

# Image files larger than this will be split before being wrapped
# into a package.
MAX_FILE_SIZE = (6 * 1024 * 1024 * 1024) # 6GB
# They will be split into segments of this size
SEGMENT_SIZE = '5G'

def main(args):
    if args.UUID and args.UUID != "":
        products = [args.UUID]
    elif args.SUITE and args.MAJOR_VERSION:
        products = read_suite(args.SUITE, args.MAJOR_VERSION)
    else: 
        print("You need to specify --product-uuid or --suite and --major-version")
        sys.exit(255)

    dist_types = ['full-products']
    if args.UPDATES:
        dist_types.append('updates')
    if args.UPDATES_ONLY:
        dist_types.remove('full-products')

    check_create_download_dirs(args.DOWNLOAD_DIR, dist_types)

    # Store this somewhere independent so we can access it between runs
    cache_dir = subprocess.check_output(['getconf', 'DARWIN_USER_CACHE_DIR']).strip()

    token_file = os.path.join(cache_dir, '.nativeinstruments_token')

    # We need a token to talk to the NI API. See if we stashed it on a previous run
    if not os.path.isfile(token_file):
        # We need to grab the token from Native Access
        if args.DOWNLOAD_ONLY or args.PACKAGES:
            na_location = os.path.join(args.DOWNLOAD_DIR, 'Native Access')
        else:   
            na_location = ('/Applications')

        install_native_access(args.DOWNLOAD_DIR, na_location)

        token = get_bearer_token(os.path.join(na_location, 'Native Access.app/Contents/MacOS/Native Access'))
        # Save it for next time
        with open(token_file, 'w') as tf:
            tf.write(token)
    else:
        # Read the token from our cache
        print("Reading token file: {}".format(token_file))
        with open(token_file, 'r') as tf:
            token = tf.read()

    # Stash our auth token.
    AUTH_HEADER['Authorization'] = 'Bearer ' + token

    # Maintain a list of the packages we create
    report_data = []

    for prod in products:
        for dist_type in dist_types:
            try:
                artifacts = get_artifacts(prod, dist_type)

                latest = get_latest_artifacts(artifacts)
                
                for art in latest:
                    # If we're in 'file templating mode' just do our stuff
                    if args.AUTOPKG_OVERRIDE:
                        template_override_file(args.OVERRIDE_SOURCE, args.OVERRIDE_DEST, art)
                        time.sleep(1)
                        continue

                    files = process_artifact(art, dist_type=dist_type, download_dest=args.DOWNLOAD_DIR,
                                             force_download=(args.DOWNLOAD_ONLY or args.PACKAGES))
                    if not files: 
                        # This artifact has nothing for us to install
                        continue
                    for (candidate, version) in files:
                        if args.DOWNLOAD_ONLY or is_installed(candidate, version):
                            # Already installed, or user has requested no installation
                            report_data.append({'download_path': candidate, 'version': version})
                            continue
                        if args.PACKAGES and candidate.endswith('.iso'):
                            # Wrap the ISO in a .pkg installer
                            (final_pkg, final_version) = wrap_iso(candidate, version, 
                                                                  dest=os.path.join(args.DOWNLOAD_DIR, 
                                                                  dist_type, '_packages'))
                            # If the variables are empty, nothing was created
                            if final_pkg and final_version:
                                report_data.append({'package_path': final_pkg, 'version': final_version})

                            continue
                        path = None # Set this to something so we can reference it in the finally block
                        try:
                            path, pkg = attach_image(candidate)
                            if args.PACKAGES:
                                (final_pkg, final_version) = copy_pkg(os.path.join(path, pkg), version,
                                                                      os.path.join(args.DOWNLOAD_DIR, 
                                                                      dist_type, '_packages'))
                                # If the variables are empty, nothing was created
                                if final_pkg and final_version:
                                    report_data.append({'package_path': final_pkg, 'version': final_version})
                            else:
                                install_pkg(path + '/' + pkg, candidate, version)

                        except subprocess.CalledProcessError as err:
                            print("INSTALL FAILED: {} ({})".format(pkg, err))
                            continue
                        finally:
                            if path:
                                unmount(path)
                            if not args.PRESERVE:
                                os.unlink(candidate)
            except urllib2.HTTPError as err:
                sys.stderr.write("{}\n".format(err))
                continue
    if report_data != []:
        # If we created something, report on it
        return report_data    


def template_override_file(source, dest_dir, artifact):
    source_type = os.path.basename(source).split('.')[-2]
    out_file = "{}.{}.recipe".format(os.path.join(dest_dir, artifact['title'].replace(' ', '')),
                                    source_type)
    
    in_plist = plistlib.readPlist(source)
    
    in_plist['Identifier'] = "local.{}.{}".format(source_type, artifact['title'].replace(' ', ''))
    in_plist['Input']['NAME'] = artifact['title']
    in_plist['Input']['PRODUCT_UUID'] = artifact['upid']

    plistlib.writePlist(in_plist, out_file)
    print("Wrote:", out_file)


def check_create_download_dirs(d_dir, dist_types):
    for atype in dist_types:
        if not os.path.isdir(d_dir + '/' + atype):
            os.makedirs(d_dir + '/' + atype)


def get_bearer_token(path):
    strings = subprocess.check_output(['strings', path]).split('\n')
    token = [s for s in strings if s.startswith('eyJhbGciOiJSUzI1NiI')]
    return token[0]


def install_native_access(downloads, install_dest):
    print('Downloading Native Access...')
    fetch(NATIVE_ACCESS_URL, dest=downloads + '/native-access.dmg')
    path, pkgs = attach_image(downloads + '/native-access.dmg')

    dest = os.path.join(install_dest, 'Native Access.app')
    
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    
    print('Installing Native Access...')
    shutil.copytree(os.path.join(path, 'Native Access.app'), dest)
    unmount(path)


def read_suite(suite, version):
    suite_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                'product_lists', "{}_{}.txt".format(suite, version))
    print("Reading", suite_file)
    id_list = None
    with open(suite_file, 'r') as f:
        id_list = f.readlines()
        # Remove comments and newlines and blank lines
        id_list = [f.strip() for f in id_list if ( not f.startswith('#') and not f == '\n')]
        # Remove anything before a final comma
        id_list = [f.split(',')[-1] if ',' in f else f for f in id_list]
    return id_list


def is_installed(target_file, version):
    receipts = INSTALL_RECEIPTS
    ident = '{}-{}'.format(os.path.basename(target_file), version)
    if not os.path.isfile(receipts):
        print("{} is not installed".format(ident))
        return False
    else:
        with open(receipts, 'r') as rcpt:
            result = ident in rcpt.read().split('\n')
        if result:
            print("{} is installed already".format(ident))
        else:
            print("{} is not installed".format(ident))
        return result


def attach_image(img):
    if not os.path.isfile(img) or not img.endswith(('.iso', '.dmg')):
        return None

    output = subprocess.check_output(['hdiutil', 'attach', '-nobrowse', img])
    mounted_path = output.split("\t")[-1].strip()
    pkgs = [a for a in os.listdir(mounted_path) if a.endswith('.pkg')]
    try:
        pkgs = pkgs[0]
    except IndexError: # There may not be any packages...
        pkgs = None
    return (mounted_path, pkgs)


def unmount(path):
    subprocess.check_call(['hdiutil', 'detach', path])


def install_pkg(package, from_file, version):
    # Will raise a subprocess.CalledProcessError in case of failure
    print("Installing: ", package)
    receipts = INSTALL_RECEIPTS
    ident = '{}-{}'.format(os.path.basename(from_file), version)
    cmd = ['/usr/sbin/installer', '-pkg', package, '-target', '/']
    subprocess.check_call(cmd)
    with open(receipts, 'a+') as rcpt:
        rcpt.write('{}\n'.format(ident))

def copy_pkg(package, version, dest):
    # Will raise a subprocess.CalledProcessError in case of failure
    print("Copying: ", package)
    if not os.path.isdir(dest):
        os.mkdir(dest)
    out_pkg = canonicalise_pkg_name(package, version)
    cmd = ['cp', package, os.path.join(dest, out_pkg)]
    subprocess.check_call(cmd)

    return((os.path.join(dest, out_pkg), version))

def wrap_iso(iso, version, dest):    
    # Set up some names of things
    image_name = os.path.basename(iso)
    pkg_name = image_name[:-4]
    out_file = os.path.join(dest, canonicalise_pkg_name(pkg_name, version))

    if os.path.isfile(out_file):
        print("{} exists".format(out_file))
        return((None, None))

    if not os.path.isdir(dest):
        os.makedirs(dest)

    tmp_dir = tempfile.mkdtemp(suffix="NativeInstruments", dir=dest)

    pkg_scripts = os.path.join(tmp_dir, 'Scripts')
    
    os.mkdir(pkg_scripts)

    if os.path.getsize(iso) > MAX_FILE_SIZE:
        # The image is too big to fit in a macos install package
        # so we'll need to split it.

        # First convert to UDZO format
        dmg_path = os.path.join(tmp_dir, pkg_name + '.dmg')
        subprocess.check_call(['hdiutil', 'convert', '-format', 'UDZO', '-o', dmg_path, iso])
        
        # Then split it up
        subprocess.check_call(['hdiutil', 'segment', '-segmentSize', SEGMENT_SIZE, '-o', 
                               os.path.join(pkg_scripts, pkg_name + '.split'), dmg_path])

        image_name = image_name.replace('.iso', '.split.dmg')
    else:
        # Move iso into package folder
        shutil.move(iso, os.path.join(pkg_scripts, os.path.basename(iso)))

    preinstall_script = r"""#!/bin/sh
iso="{}"
set -euo pipefail
echo "Mounting $iso..."
vol="$(hdiutil attach -nobrowse "${{iso}}"  | tail -1 | awk -F '\t' '{{print $3}}')"

pkg="$(ls "${{vol}}" | grep '\.pkg$' | egrep -v 'Part \d+\.pkg' | head -1)"

if [ ! -z "${{pkg}}" ]
then
    echo "Installing ${{pkg}}..."
    installer -pkg "${{vol}}/${{pkg}}" -target / -dumplog  
    sleep 5
else
    echo "Can't find a package at ${{vol}}"
fi
diskutil unmount "${{vol}}"
""".format(image_name)

    with open(os.path.join(pkg_scripts, 'preinstall'), 'w') as f:
        f.write(preinstall_script)

    subprocess.check_call(['chmod', '0755', 
                           os.path.join(pkg_scripts, 'preinstall')])

    subprocess.check_call(['pkgbuild', '--nopayload', 
                           '--scripts', pkg_scripts,
                           '--version', version,
                           '--id', 'com.nativeinstruments.' + pkg_name,
                           out_file])

    shutil.rmtree(tmp_dir)

    return((out_file, version))


def canonicalise_pkg_name(name, version):
    # Remove .pkg - we will add it back after manipulation
    if name.endswith('.pkg'):
        name = name[:-4]
    # Get rid of spaces
    name = name.replace(' ', '_')
    # Remove any path components before the name
    name = os.path.basename(name)
    return name + '-' + version + '.pkg'


def process_artifact(artifact, dist_type, download_dest, force_download=False):
    # No Windows, thanks.
    if not artifact['platform'] in ['mac_platform', 'all_platform']:
        return None

    print("{}, {}".format(artifact['title'], artifact['version']))

    files_to_process = artifact['files']
    files_to_return = []
    
    # If there is an 'installer_type' and an 'iso_type', we just want the installer
    if [ f for f in artifact['files'] if f['type'] == 'installer_type' ] != []:
        print("Ignoring ISO installers as a DMG is available")
        files_to_process = [ f for f in artifact['files'] if f['type'] == 'installer_type' ]

    for afile in files_to_process:
        # We don't want 'downloader_type' files - just ISOs, updaters and installers
        if not afile['type'] in ['iso_type', 'update_type', 'installer_type']:
            continue

        url = get_download_url(afile)
        print('{}, {}M, {}'.format(
            afile['target_file'], afile['filesize']/1024/1024, url))
        
        if force_download is True or (not is_installed(afile['target_file'], artifact['version'])):
            outfile = os.path.join(download_dest, dist_type, afile['target_file'])
            if os.path.isfile(outfile) and not afile['filesize'] > os.path.getsize(outfile):
                files_to_return.append((outfile, artifact['version']))
                continue

            print("Downloading: ", afile['target_file'])
            fetch(url, headers=PROTOBUF_HEADERS, dest=outfile)
            files_to_return.append((outfile, artifact['version']))

    return files_to_return

        
def get_download_url(a_file):
    # The 'url' attribute of a_file leads to an XML metalink
    # document which contains various information about the download
    # including the the actual download URL we need.
    meta_url = BASEURL + '/v1/download/' + a_file['url']
    resp = fetch(meta_url, headers=METALINK_HEADERS)
    tree = ET.fromstring(resp.read())
    url = tree.findall('.//{urn:ietf:params:xml:ns:metalink}url')[0].text
    return url


def get_artifacts(prod, dist_type):
    if dist_type not in ['full-products', 'updates']:
        return None
    url = BASEURL + '/v1/download/' + dist_type + '/' + prod
    resp = fetch(url, headers=JSON_HEADERS)
    resp_data = json.loads(resp.read())['response_body']
    return resp_data['artifacts']


def get_latest_artifacts(artifacts):
    sorted_versions = sorted(
        artifacts, key=lambda k: LooseVersion(k['version']))
    latest_version_string = sorted_versions[-1]['version']
    latest = [v for v in sorted_versions if v['version']
              == latest_version_string]
    return latest

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

@retry((SocketError, urllib2.HTTPError), tries=4, delay=2, backoff=2)
def fetch(url, dest=None, data=None, headers=None):
    """ Fetch `url`.
        If `data` is present send a POST request, otherwise GET
        If `dest` is present, store the result there, otherwise
        return a file-like object.
    """
    myheaders = {}
    myheaders.update(USER_AGENT)
    myheaders.update(AUTH_HEADER)

    if headers is not None:
        myheaders.update(headers)

    #   sys.stderr.write("fetch: {}\n".format(url))
    if data:
        # If data is serialisable, send it as json
        try:
            data = json.dumps(data)
        except:
            # Just send whatever we were passed, raw
            pass
    req = urllib2.Request(url, headers=myheaders, data=data)

    resp = urllib2.urlopen(req)

    if dest:
        with open(dest, 'wb') as fp:
            shutil.copyfileobj(resp, fp)
    else:
        return resp



if __name__ == '__main__':
    main(process_args())
