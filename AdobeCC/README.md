Adobe CC Packages - AutoPkg Repository
======================================

This repo builds on the work at https://github.com/mosen/ccp-recipes, but includes some extras to provide us a fully automated workflow. Specifically, we provide:

* `CreativeCloudApp.flatpkg.recipe` - A recipe which flattens the bundle packager produced by CCP
* `CreativeCloudApp.flatpkg.jss.recipe` - Uses JSSImporter to upload the flat package to a distribution server
* `generate_recipes.py` - A script which will generate a recipe file for each CC application, for use by autopkg
* `recipes-to-package.txt` - A hand-cranked list of the recipes we actually want to package

Usage
=====

To build all the recipes, you will need to

# Install Autopkg
# Install JSSImporter (at least v1.0.2)
# Set up details for your JSS/JDS/JCDS in ~/Library/Preferences/com.github.autopkg.plist
# Run `generate_recipes.py`
# Run `autopkg run -v --recipe-list=recipes-to-package.txt`

This should:
# Generate recipe files for all of the latest releases of the CC applications
# Package those which are listed in `recipes-to-package.txt`.
# Upload the packages to your JSS
# Create policies and smartgroups as required 
