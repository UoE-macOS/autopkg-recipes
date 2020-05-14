# Native Instruments Autopkg Recipes

## Introduction
Native Instruments' various products are usually installed via a GUI application called 'Native Access'. This is convenient for individual users but, given that there is no unattended option, very inconvenient for administrators of managed environments.

This repo provides an AutoPkg processor which emulates enough of the behaviour of the Native Access application to allow AutoPkg to download the product artefacts (typically ISO images) so that we can deploy them in a managed environment. 

## Where are the recipes?
`NativeInstrumentsProduct.{pkg, download, munki}.recipe` are generic recipes using the `NIDownloadProvider` processor. To use the recipes, you need to generate an override for each specific product that you want to install.

Suites (such as Komplete) are made up of numerous products, and this repo includes a command that you can use to easily generate your own set of override files, one for each product in a suite that you want to package.

`NativeInstrumentsProduct.download.recipe`

The `.download` recipe just downloads the product disk images (some are available as `.dmg` files, some are `.iso`). Its main use is to chain other recipes onto.

`NativeInstrumentsProduct.munki.recipe`

The `.munki` recipe can be used to import the downloaded images directly into munki. Thanks to <a href="https://github.com/andrewvalentine" target="_blank">@andrewvalentine</a> for contributing to this.

`NativeInstrumentsProduct.pkg.recipe`

The `.pkg` recipe can be used if you want to generate a package for each product that can be directly installed by less-intelligent package management tools, such as JAMFPro. 

`NativeInstrumentsSuiteNetInstall.pkg.recipe`

This can be used to generate a single, payloadless, package which contains a postinstall script to install a whole suite, directly from Native Instruments' CDN, on a client machine.

## How to use this repo

1. First, you need to generate an override file: 
```
autopkg make-override NativeInstrumentsProduct.pkg.recipe

or 

autopkg make-override NativeInstrumentsProduct.munki.recipe
```
__You now need to edit the override file__ created by this step, to add the username and password of your Native Instruments account. If you like, you can also specify a custom Download location or (if you have used the `.munki` recipe) set some munki variables appropriate to your environment. 

__warning__: Your Native Instruments password will be stored in plaintext the override files. Please make sure you are doing your packaging on a secure machine. Keychain integration is a Work In Progress!

2. Next, use the helper tool to use this file as a template to generate overrides for each of the products you want to package. This will simply copy the template override file you made in step 1 multiple times, replacing the relevant name and UUID for each product. the example below assumes you are using the `.pkg` recipe: be sure to replace `--template-override-source` with the correct file.
```
mkdir ~/Library/AutoPkg/RecipeOverrides/NativeInstruments
python ~/Library/AutoPkg/RecipeRepos/com.github.uoe-macos.autopkg-recipes/Native\ Instruments/native_instruments_helper.py\
                --template-autopkg-override \
                --template-override-source ~/Library/AutoPkg/RecipeOverrides/NativeInstrumentsProduct.pkg.recipe \
                --template-override-dest-dir ~/Library/AutoPkg/RecipeOverrides/NativeInstruments \
                --username <NI Username> --password <NI Password>
                --suite=komplete --major-version=11
```
NB: The `--suite` and `--major-version` arguments rely on there being a file named \<suite\>\_\<major_version\>.txt in the product_lists folder. So far we have such lists for Komplete Standard 11 and Komplete Standard 12. Further contributions are welcome - please open a pull request.

If you like, you can instead use the `--product-uuid` argument to template an override file for a single product.

3. Now that you have a folder containing the override files you need, you can throw autopkg at it: 
```
autopkg run ~/Library/AutoPkg/RecipeOverrides/NativeInstruments/*
```
and wait a while.

Note that, if you are a Munki user, you only need to run the `.munki` recipes:
```
autopkg run ~/Library/AutoPkg/RecipeOverrides/NativeInstruments/*.munki.recipe
```

## Processor Configuration
Some configuration variables are available in the `NIDownloadProvider` processor:

* `product_uuid`: UUID of the product for which you want a package. 
* `downloads`: Folder to which to download items.
* `version`: This does nothing. You get the latest version. 

### Product UUIDs
I haven't been able to find any way to programatically determine the list of products that make up a suite (eg Komplete), so the processor needs to be given the UUIDs of the products you want to package. You can see the list of UUIDs for Komplete 11 and Komplete 12 in the `product_lists` directory. 

How do you get the product UUIDs for a given suite? Good question. The best place I can suggest is to look in the files in `/Library/Application Support/Native Instruments/Service Center` on a machine with the suite installed. The XML files therein contain the UPIDs for most of the installed products; however, not every product leaves behind an XML file and we have had to resort to more devious means to determine the others. We are fairly confident the list for Komplete 12 is, um, complete.

## Implementation
The `NIDownloadProvider.py` processor is a thin wrapper around the `native_instruments_helper.py` tool in this directory. `native_instruments_helper.py` can be used on its own to perform downloads or even full installs of Native Instruments products and suites. Run it for more information: `python ./native_instruments_helper.py --help`

## DISCLAIMER
This recipe and associated helper tool use an undocumented and unsupported API. They may break at any time. Please refer to this repository's [LICENSE](https://github.com/UoE-macOS/autopkg-recipes/blob/master/LICENSE)

## CREDITS
Many thanks to those who have contributed to making this a useful repo. @neilmartin83, @achmelvic, @andrewvalentine @lrhodes at macadmins have all provided invaluable help, advice and camaraderie.
