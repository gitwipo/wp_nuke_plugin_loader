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
Add the basic paths so everythings also works in the commadline.

file=init.py
"""


__author__ = "Wilfried Pollan"
__current_file__ = __file__


# Imports
import os
import codecs
import json
import logging.config
import wp_plugin_loader


# Logging setup
PREFSTYPE = ".json"
LOGGING_CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(os.path.realpath(__current_file__))),
    "configs",
    "logging" + PREFSTYPE,
)
with codecs.open(LOGGING_CONFIG, "r", encoding="utf-8") as fobj:
    config = json.load(fobj)
logging.config.dictConfig(config["logging"])


# Run
loader = wp_plugin_loader.LoadPlugins()
loader.add_python_paths()
loader.add_tool_paths()
