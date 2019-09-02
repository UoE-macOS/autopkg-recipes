#!/bin/sh

# Set preferences for Projucer to disable analytics & auto-update,
# and to point to the correct installation location for the JUCE 
# headers.

# This script expects to be run as a login script by the Jamf Pro server
# - as such it expects the currently-logging-in-username to be passed
# as the third argument.

# These variables will be templated in by the 'git2jss' tool

# Date: @@DATE
# Version: @@VERSION
# Origin: @@ORIGIN
# Link: @@ORIGIN/commit/@@VERSION
# Released by JSS User: @@USER

user_name="${3}"
path_to_juce='/Applications/JUCE'
projucer_prefs_dir="/Users/${user_name}/Library/Application Support/Projucer"

# Create path to our prefs file if it doesn't already exist
if [ ! -d "${projucer_prefs_dir}" ]
then
  mkdir -p "${projucer_prefs_dir}"
  chown "${user_name}" "${projucer_prefs_dir}"
fi

# Settings to set our default module path and disable usage data
projucer_settings_file="`cat << EOF
<?xml version="1.0" encoding="UTF-8"?>

<PROPERTIES>
  <VALUE name="PROJECT_DEFAULT_SETTINGS">
    <PROJECT_DEFAULT_SETTINGS jucePath="${path_to_juce}" defaultJuceModulePath="${path_to_juce}/modules"/>
  </VALUE>
  <VALUE name="dontAskAboutJUCEPath" val="1"/>
  <VALUE name="license">
    <license type="GPL" applicationUsageData="disabled" username="GPL mode"
             email="" authToken=""/>
  </VALUE>
</PROPERTIES>
EOF`"

echo "$projucer_settings_file" > $projucer_prefs_dir/Projucer.settings
status=$?

if [ $status == 0 ]
then
  echo "Set preferences successfully"
else
  echo "Failed"
fi

exit $status
