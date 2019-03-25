# Wwise AutoPkg Recipe

## Introduction
[Wwise](https://www.audiokinetic.com/products/wwise/) is installed via an opaque [Electron](https://electronjs.org/) application called the Wwise launcher. This recipe takes the approach of remiplementing enough of the behaviour of the installer application to download the necessary archives and install them to a package root, then create a package.

The Wwise application itself is a Windows application which is packaged to run on macOS under [Crossover](https://www.codeweavers.com/products). This recipe also patches the install so that the necessary extra Windows libraries are downloaded on first run without user intervention

## Configuration
Several configuration variables are available:

* `VERSION`: The version to install. Setting this to LATEST or an empty string will give you the latest version available
* `EMAIL`: If you have a Wwise login and wish to access protected assets, set this variable to your email address...
* `PASSWORD`: ... and this one to the relevant password.
* `INSTALL_STYLE`: Should be set to `mini` or `maxi`. `mini` will give you just the authoring packages, which is all that is required in our environment. `maxi` (experimental) will install all Wwise packages that are available, including SDKs for numerous platforms. If your email address has access to restricted content, `maxi` may install it, but this hasn't been tested.

## Implementation
The `WwiseInstallProvider.py` processor is a thin wrapper around the `wwise_helper.py` tool in this directory. `wwise_helper.py` can be used on its own and has various options for controlling the installation. Run it directly for more information: `python wwise_helper.py --help`

## DISCLAIMER
This recipe and associated helper tool use an undocumented and unsupported API. They may break at any time. Please refer to this repository's [LICENSE](https://github.com/UoE-macOS/autopkg-recipes/blob/master/LICENSE)
