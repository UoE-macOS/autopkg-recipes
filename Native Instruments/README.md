# Native Instruments Autopkg Recipes

## Introduction
Native Instruments is usually installed via a GUI application called 'Native Access'. This repo provides an AutoPkg processor which emulates enough of the behaviour of Native Access to allow AutoPkg to download product artefacts and wrap them into packages.

You need to provide autopkg with the UUID of the product you want to package - I can't find any way of deriving this programmatically from the name. 

## Recipes
`NativeInstrumentsProduct.pkg.recipe` is an generic recipe using the `NIDownloadProvider` processor. The repo includes a command to generate your own override files, one for each product that you want to package.

## How to use this repo

1. First, you need to generate an override file: `autopkg make-override NativeInstrumentsProduct.pkg.recipe`
2. Next, use the helper tool to generate overrides for all the products you want to package. This will simply copy the template override file you made in step 1, replacing the relevant info for each product.
```
~/Library/AutoPkg/RecipeRepos/com.github.uoe-macos.autopkg-recipes/Native\ Instruments/native_instruments_helper.py\
                --template-autopkg-override \
                --template-override-source ~/Library/AutoPkg/RecipeOverrides/NativeInstrumentsProduct.pkg.recipe \
                --template-override-dest-dir ~/Library/AutoPkg/RecipeOverrides/NativeInstruments \
                --suite=komplete --major-version=11
```
3. Now that you have the override files you need, you can throw autopkg at it: `autopkg run ~/Library/AutoPkg/RecipeOverrides/NativeInstruments/*`

NB: The `--suite` and `--major-version` arguments rely on there being a file named <suite>_<major_version>.txt in the product_lists folder. So far I only have such a list for Komplete 11 - contributions welcome.
You can instead use the `--product-uuid` argument to template and override file for a single product.


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
