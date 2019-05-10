# Native Instruments Autopkg Recipes

## Introduction
Native Instruments is usually installed via a GUI application called 'Native Access'. This repo provides an AutoPkg processor which emulates enough of the behaviour of Native Access to allow AutoPkg to download all the packages that make up and install of a Native Instruments package.

Currently only Komplete 11 is supported - open an issue if you'd like something else: it's simple in principle.

## Recipes
`Komplete11.pkg.recipe` is an example reciupe using the `NIDownloadProvider` processor. It will download all products for Komplete 11, and produce produce installable .pkg files from those that do not have them.

## Configuration
Some configuration variables are available in the `NIDownloadProvider` processor:

* `version`: The version to install. Only '11' is currently supported
* `product`: The product to install. Only 'Komplete' is currently supported
* `downloads`: Folder to download items to

### Product Lists
I haven't been able to find any way to programatically determine the list of products that make up a suite (eg Komplete), so to help the processor we need to provide the lists as text files. You can see the list for Komplete 11 in the `product_lists` directory. To add a new product, or a new version of an existing product, just create a new file called PRODUCT_VERSION.txt in that directory and pass the PRODUCT and VERSION to autopkg. For example, you could create `product_lists/komplete_12.txt` and then override the `Komplete11.pkg.recipe` recipe, setting VERSION to 12.

How do you get the identifiers? Good question. The best place I can suggest is to look in the preference files in `/Library/Preferences.com.native-instruments*` on a machine with the suite that you want installed.

## Implementation
The `NIDownloadProvider.py` processor is a thin wrapper around the `native_instruments_helper.py` tool in this directory. `native_instruments_helper.py` can be used on its own to perform downloads or even full installs of (currently) Komplete 11. Run it for more information: `python ./native_instruments_helper.py --help`

## DISCLAIMER
This recipe and associated helper tool use an undocumented and unsupported API. They may break at any time. Please refer to this repository's [LICENSE](https://github.com/UoE-macOS/autopkg-recipes/blob/master/LICENSE)
