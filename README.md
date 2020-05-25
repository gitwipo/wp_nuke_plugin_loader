# Nuke Plugin Loader

## About

This Plugin Loader is inspired by different exiting tools for Nuke which are also for automatic loading gizmos, toolsets and scripts.
The script load all tools in the defined plugin path based on the folder structure into the menu and toolbar.

## Features

- Add all paths until it reaches the exclude keywords
- Load gizmos, toolsets scripts based on the folder structure
- Adjustable logging (console and file)
- All preferences in a json config file

## Future Development

- Manage tools load state from Nuke UI
- Change menu path
- Add Custom loader commands for the tools

## Limitations

- To load python and tcl scripts a menu.py or/and init.py is needed.
Check the tool install help for the specific commands.

## Usage

### Setup

To start using the plugin loader:

1. Download the whole folder into your HOME/.nuke folder.

2. Setup Nuke so it finds the tools.

    a) If you do not have a *HOME/.nuke/init.py* yet -> Copy the *init.py.example* to *HOME/.nuke/init.py*
    
    b) You already have a *HOME/.nuke/init.py* -> Copy the line:

        nuke.pluginAddPath("./wp_nuke_plugin_manager")

    to your *HOME/.nuke/init.py*

3. Default root folder for:  
    gizmos, toolsets, python and tcl scripts is: **plugins**  
    python modules is: **python**  
    This settings can be changed in: *configs/preferences.json*

### Configuration

All adjustable parameter are defined in: *configs/preferences.json*  
All path are defined for all three mayor platforms. All set environment variables that are set at Nuke start can be used in the config.  
The basic syntax is: **${ *env name* }**

The follwing setting can be changed:

- ***PLUGINS_PATH***
- ***PYTHON_PATH***
- ***INCLUDES*** -> The files to include
- ***EXCLUDES*** -> Don't search inside this folder
- ***SPECIAL_FILES*** -> If found will jump to next folder
- ***MENU*** -> The root menus for the plugins

## Licensing

Apache License, Version 2.0

## Authors

Wilfried Pollan - Maintainer

## Versioning

See https://semver.org

0.1.0 - First release - Adds and loads plugins (qizmos, toolsets, scripts) 
