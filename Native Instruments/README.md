# Native Instruments Autopkg Recipes

## Introduction
Native Instruments is usually installed via a GUI application called 'Native Access'. This repo provides an AutoPkg processor which emulates enough of the behaviour of Native Access to allow AutoPkg to download all the packages that make up an install of a Native Instruments product.

Currently only Komplete 11 is supported - open an issue if you'd like something else: it's simple in principle.

## Recipes
`Komplete11.pkg.recipe` is an example recipe using the `NIDownloadProvider` processor. It will download all install media for Komplete 11, and produce produce installable .pkg files from ISOs where necessary (by wrapping the ISO in a .pkg).

## Configuration
Some configuration variables are available in the `NIDownloadProvider` processor:

* `version`: The version to install. Only '11' is currently supported.
* `product`: The product to install. Only 'Komplete' is currently supported.
* `downloads`: Folder to which to download items.

## Implementation
The `NIDownloadProvider.py` processor is a thin wrapper around the `native_instruments_helper.py` tool in this directory. `native_instruments_helper.py` can be used on its own to perform downloads or even full installs of (currently) Komplete 11. Run it for more information: `python ./native_instruments_helper.py --help`

## DISCLAIMER
This recipe and associated helper tool use an undocumented and unsupported API. They may break at any time. Please refer to this repository's [LICENSE](https://github.com/UoE-macOS/autopkg-recipes/blob/master/LICENSE)
