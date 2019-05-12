# Native Instruments Autopkg Recipes

## Introduction
Native Instruments is usually installed via a GUI application called 'Native Access'. This repo provides an AutoPkg processor which emulates enough of the behaviour of Native Access to allow AutoPkg to download product artefacts and wrap them into packages.

You need to provide autopkg with the UUID of the product you want to package - I can't find any way of deriving this programmatically from the name. 

## Recipes
`NativeInstrumentsProduct.pkg.recipe` is an generic recipe using the `NIDownloadProvider` processor. You can override it and insert the UUID of the product you want to package in the PRODUCT_UUID variable.

## Configuration
Some configuration variables are available in the `NIDownloadProvider` processor:

* `product_uuid`: The product to install. Only 'Komplete' is currently supported.
* `downloads`: Folder to which to download items.
* `version`: This does nothing. You get the latest version. 

### Product UUIDs
I haven't been able to find any way to programatically determine the list of products that make up a suite (eg Komplete), so the processor needs to be given the UUID of the product you want to package. You can see the list of UUIDs for Komplete 11 in the `product_lists` directory. 

How do you get the UUIDs for a given suite? Good question. The best place I can suggest is to look in the preference files in `/Library/Preferences.com.native-instruments*` on a machine with the suite that you want installed.

## Implementation
The `NIDownloadProvider.py` processor is a thin wrapper around the `native_instruments_helper.py` tool in this directory. `native_instruments_helper.py` can be used on its own to perform downloads or even full installs of Native Instruments products and suites. Run it for more information: `python ./native_instruments_helper.py --help`

## DISCLAIMER
This recipe and associated helper tool use an undocumented and unsupported API. They may break at any time. Please refer to this repository's [LICENSE](https://github.com/UoE-macOS/autopkg-recipes/blob/master/LICENSE)
