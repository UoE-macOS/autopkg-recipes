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

1. Install Autopkg
2. Install JSSImporter (at least v1.0.2)
3. Set up details for your JSS/JDS/JCDS in ~/Library/Preferences/com.github.autopkg.plist
4. Run `generate_recipes.py`
5. Run `autopkg run -v --recipe-list=recipes-to-package.txt`

This should:
6. Generate recipe files for all of the latest releases of the CC applications
7. Package those which are listed in `recipes-to-package.txt`.
8. Upload the packages to your JSS
9. Create policies and smartgroups as required 
