#!/usr/bin/env python

# Copyright 2016 Mosen/Tim Sutton
#
# Modifications by gkluoe
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
import json
import unicodedata
import urllib2
from urllib import urlencode

CCM_URL = 'https://prod-rel-ffc-ccm.oobesaas.adobe.com/adobe-ffc-external/core/v4/products/all'
BASE_URL = 'https://prod-rel-ffc.oobesaas.adobe.com/adobe-ffc-external/aamee/v2/products/all'

def add_product(products, product):
    if product['id'] not in products:
        products[product['id']] = []

    products[product['id']].append(product)


def feed_url(channels, platforms):
    """Build the GET query parameters for the product feed."""
    params = [
        ('payload', 'true'),
        ('productType', 'Desktop'),
        ('_type', 'json')
    ]
    for ch in channels:
        params.append(('channel', ch))

    for pl in platforms:
        params.append(('platform', pl))

    return BASE_URL + '?' + urlencode(params)

def fetch(channels, platforms):
    """Fetch the feed contents."""
    url = feed_url(channels, platforms)
    print('Fetching from feed URL: {}'.format(url))

    req = urllib2.Request(url, headers={
        'User-Agent': 'Creative Cloud',
        'x-adobe-app-id': 'AUSST_4_0',
    })
    data = json.loads(urllib2.urlopen(req).read())

    return data

def dump(channels, platforms):
    """Save feed contents to feed.json file"""
    url = feed_url(channels, platforms)
    print('Fetching from feed URL: {}'.format(url))

    req = urllib2.Request(url, headers={
        'User-Agent': 'Creative Cloud',
        'x-adobe-app-id': 'AUSST_4_0',
    })
    data = urllib2.urlopen(req).read()
    with open(os.path.join(os.path.dirname(__file__), 'feed.json'), 'w+') as feed_fd:
        feed_fd.write(data)
    print('Wrote output to feed.json')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'dump':
        dump(['ccp_hd_2', 'sti'], ['osx10', 'osx10-64'])
    else:
        data = fetch(['ccp_hd_2', 'sti'], ['osx10', 'osx10-64'])
        products = {}
        for channel in data['channel']:
            for product in channel['products']['product']:
                add_product(products, product)

        for sapcode, productVersions in products.iteritems():
            print("SAP Code: {}".format(sapcode))

            # Grab the 'last' version of this product. Really we should
            # try to work out which is the latest but for the moment this
            # seems to give us that.
            productVersions = [productVersions[-1]]
            for product in productVersions:
                base_version = product['platforms']['platform'][0]['languageSet'][0].get('baseVersion')
                if not base_version:
                    base_version = None 

                name = unicodedata.normalize("NFKD", product['displayName'])
                #print("\t{0: <60}\tBaseVersion: {1: <14}\tVersion: {2: <14}".format(
            
            # Do our best to normalise names to end with 'CC2018'
            # where it makes sense to do so, and remove spaces.
            if not name.startswith('Adobe'):
                name = 'Adobe' + name
            if name.endswith(('CC', 'DC')):
                name += '2018'
            elif not (name.endswith(')') or name[-1].isdigit()):
                name += 'CC2018'
            name = name.replace(" ","")

            print("{0}\t{1: <60}\tBaseVersion: {2: <14}\tVersion: {3: <14}".format(
                    sapcode,
		    name,
                    base_version or "N/A",
                    product['version']
                ))
		
        
            # Write out a recipe file for each product. We're not going to want
            # to package all of them, but this gives us the opportunity to review and
            # choose the ones we want.
            output = ""
            with open('AdobeCCTemplate.tmpl', 'r') as template:
                output = template.read()

            output = output.format(**{'sapcode': sapcode, 'name':name, 'base_version': base_version or ""})

            with open('GeneratedRecipes/'+name+'.jss.recipe', 'w') as outfile:
                    outfile.write(output)
       
            print("")
