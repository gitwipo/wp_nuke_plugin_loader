#!/usr/bin/env python

# Copyright 2020 Wilfried Pollan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   # http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Module for loading and managing Nuke plugins.

file=wp_plugin_loader.py

Load nuke plugins:
- Toolsets
- Gizmos
- Python tools and panels
- OFX tools

:TODO:
Manage plugins:
- Disable
- Menu path
- Shortcuts
"""


__author__ = "Wilfried Pollan"
__current_file__ = __file__


# Imports
import fnmatch
import json
import logging
import os
import re
import sys
import nuke
from string import Template


# Constants
CONFIG_TYPE = ".json"
CONFIG_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(os.path.realpath(__current_file__))), "configs"
)
PREFS_CONFIG_NAME = "preferences" + CONFIG_TYPE
PREFS_CONFIG_PATH = os.path.join(CONFIG_ROOT, PREFS_CONFIG_NAME)
PLUGIN_OVERRIDE_CONFIG_NAME = "plugin_overrides" + CONFIG_TYPE
PLUGIN_OVERRIDE_CONFIG_PATH = os.path.join(CONFIG_ROOT, PLUGIN_OVERRIDE_CONFIG_NAME)


def _convert2slash(string):
    return string.replace("\\", "/")


class LoadPlugins(object):
    """
    Query and load all plugins based on the provided configs.
    """

    def __init__(self, config_root=None):
        """
        Init loader with values from the prefs.

        :param prefs: Optional path to the preferences
        :type prefs: str
        """
        # Init logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Init nuke plugin loader.")

        # Check if pref given otherwise load the default it from the default location
        if config_root is not None and os.path.isdir(config_root):
            self.preferences = self._load_configs(
                os.path.join(config_root, PREFS_CONFIG_NAME)
            )

            # Load optional config for plugin override if exists.
            plugin_override_path = os.path.join(
                config_root, PLUGIN_OVERRIDE_CONFIG_NAME
            )
            if os.path.isfile(plugin_override_path):
                self.plugin_overrides = self._load_configs(plugin_override_path)
        else:
            self.preferences = self._load_configs(PREFS_CONFIG_PATH)

            # Load optional config for plugin override if exists.
            if os.path.isfile(PLUGIN_OVERRIDE_CONFIG_PATH):
                self.plugin_overrides = self._load_configs(PLUGIN_OVERRIDE_CONFIG_PATH)

        # Check the current platform and return resolved path
        self.plugins_path = self._resolve_platform_paths("PLUGINS_PATH")
        self.python_path = self._resolve_platform_paths("PYTHON_PATH")

        # Set regex
        includes = self.preferences["INCLUDES"]
        includes = r"|".join([fnmatch.translate(x) for x in includes]) or r"$."
        self.re_includes = re.compile(includes)
        excludes = self.preferences["EXCLUDES"]
        excludes = r"|".join([fnmatch.translate(x) for x in excludes]) or r"$."
        self.re_excludes = re.compile(excludes)

        # Get tools
        self.tools_dict = self._get_tools_files()

    def _load_configs(self, path):
        """
        Load preferences from file.

        :param path: Path to config file
        :type path: str
        """
        self.logger.info("Loading config: {0}".format(path))
        if os.path.isfile(path) and path.endswith(CONFIG_TYPE):
            try:
                with open(path) as fobj:
                    return json.load(fobj)
            except json.JSONDecodeError:
                logging.exception(
                    "The config is not a valid {0} object!\n".format(CONFIG_TYPE)
                )
                exit(1)
        else:
            logging.exception(
                "Provided config path does not exists or is not {0} file!\n".format(
                    CONFIG_TYPE
                )
            )
            exit(1)

    def _resolve_platform_paths(self, key):
        if sys.platform.startswith("linux"):
            return Template(self.preferences[key]["linux"]).safe_substitute(os.environ)
        elif sys.platform.startswith("darwin"):
            return Template(self.preferences[key]["darwin"]).safe_substitute(os.environ)
        elif sys.platform.startswith("win"):
            return Template(self.preferences[key]["win"]).safe_substitute(os.environ)

    def _get_tools_files(self):
        """
        Generate a dict with all tools.

        :return: {relative path to tool: files}
        :rtype: dict
        """
        tools_files_dict = dict()

        self.logger.debug("Searching for plugins in {0}".format(self.plugins_path))
        for root, dirs, files in os.walk(self.plugins_path, topdown=True):
            # exclude dirs
            dirs[:] = [d for d in dirs if not self.re_excludes.match(d)]

            # Check for special files and if they are present don't dive deeper.
            for special_file in self.preferences["SPECIAL_FILES"]:
                dirs[:] = [d for d in dirs if not special_file in files]

            # Here we keep only the files in includes
            files = [f for f in files if self.re_includes.match(f)]
            files = sorted(files)

            if files:
                self.logger.debug("Found: {0} > {1}".format(root, files))
                root = _convert2slash(root)[len(self.plugins_path) + 1 :]
                tools_files_dict[root] = files

        self.logger.info("Finished querying tools in: {0}\n".format(self.plugins_path))

        return tools_files_dict

    def _set_menus(self):
        """
        Query the actual menus in Nuke and set the user menus variales.
        """
        # Nuke menu and toolbar
        menubar = nuke.menu("Nuke")
        self.usermenu = menubar.addMenu("&{0}".format(self.preferences["MENU"]["nuke"]))
        toolbar = nuke.toolbar("Nodes")
        self.usertools = toolbar.addMenu(self.preferences["MENU"]["nodes"])

    @staticmethod
    def _add_gizmo_cmd(sub_menu, tool, tool_label):
        tool_command = tool
        sub_menu.addCommand(tool_label, "nuke.createNode('{}')".format(tool_command))

    def _add_nk_cmd(self, sub_menu, key, tool, tool_label):
        tool_command = "/".join([self.plugins_path, key, tool])
        sub_menu.addCommand(tool_label, "nuke.loadToolset('{}')".format(tool_command))

    def _add_py_cmd(self, key, tool, tool_path):
        self.logger.debug("Not loaded python tool: {0}".format(tool_path))

    def add_python_paths(self):
        """
        Add the paths for python modules
        """
        self.logger.info("Adding python paths.")
        nuke.pluginAddPath(self.python_path)
        self.logger.info("Added root path: {0}".format(self.python_path))
        for mod in os.listdir(self.python_path):
            if self.re_excludes.match(mod):
                continue
            mod_path = _convert2slash(os.path.join(self.python_path, mod))
            nuke.pluginAddPath(mod_path)
            self.logger.info("Added python path: {0}".format(mod_path))
        self.logger.info(
            "Finished adding python paths from: {0}\n".format(self.python_path)
        )

    def add_tool_paths(self):
        """
        Add the paths for all plugins.
        """
        self.logger.info("Adding plugin paths.")
        nuke.pluginAddPath(self.plugins_path)
        self.logger.info("Added root path: {0}".format(self.plugins_path))
        for key in self.tools_dict:
            if key is None or key is u"":
                continue
            tool_path = self.plugins_path + "/" + key
            nuke.pluginAddPath(tool_path)
            self.logger.info("Added tool path: {0}".format(tool_path))
        self.logger.info(
            "Finished adding tool paths from: {0}\n".format(self.plugins_path)
        )

    def create_tools_entry(self):
        """
        Create the menu items for the found plugins in the file system 
        and based on the settings in the preferences.
        """
        self._set_menus()
        categories = sorted([key for key in self.tools_dict])

        self.logger.info("Loading tools from: {0}".format(self.plugins_path))

        for key in categories:

            for tool in self.tools_dict[key]:
                self.logger.info("Adding: {0} > {1}".format(key, tool))

                tool_label = tool.split(".")[0]

                # Create command entry for the gizmo
                if tool.endswith(".gizmo"):
                    sub_menu = self.usermenu.addMenu(key, key)
                    sub_tools = self.usertools.addMenu(key, key)
                    self._add_gizmo_cmd(sub_menu, tool, tool_label)
                    self._add_gizmo_cmd(sub_tools, tool, tool_label)

                # Create command entry for the nk templates
                elif tool.endswith(".nk"):
                    sub_menu = self.usermenu.addMenu(key, key)
                    sub_tools = self.usertools.addMenu(key, key)
                    self._add_nk_cmd(sub_menu, key, tool, tool_label)
                    self._add_nk_cmd(sub_tools, key, tool, tool_label)

                elif tool.endswith(".py"):
                    tool_path = _convert2slash(
                        os.path.join(self.plugins_path, key, tool)
                    )
                    if tool in ["init.py", "menu.py"]:
                        continue
                    if tool_path not in self.plugin_overrides:
                        continue
                    self._add_py_cmd(key, tool, tool_path)

        self.logger.info("Finished loading tools from: {0}\n".format(self.plugins_path))


if __name__ == "__main__":
    import codecs
    import logging.config

    LOGGING_CONFIG = os.path.join(
        os.path.dirname(os.path.abspath(os.path.realpath(__current_file__))),
        "config",
        "logging" + CONFIG_TYPE,
    )
    with codecs.open(LOGGING_CONFIG, "r", encoding="utf-8") as fobj:
        config = json.load(fobj)
    logging.config.dictConfig(config["logging"])

    loader = LoadPlugins()
    loader.add_tool_paths()
    loader.add_python_paths()
