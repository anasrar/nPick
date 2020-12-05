# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "nPick",
    "author" : "Anas Rin",
    "description" : "Picker using node tree",
    "blender" : (2, 90, 0),
    "version" : (0, 1, 0),
    "location" : "Editor Type > nPick",
    "warning" : "",
    "wiki_url": "https://github.com/anasrar/..", # 2.82 below
    "doc_url": "https://github.com/anasrar/..", # 2.83 above
    "tracker_url": "https://github.com/anasrar/../issues",
    "support": "COMMUNITY",
    "category" : "Node"
}

import os
import importlib

def register():
    for dirname, subdirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
        if '__pycache__' in subdirs:
            subdirs.remove('__pycache__')

        for filename in files:
            if filename.endswith('.py') and filename != "__init__.py":
                spec = importlib.util.spec_from_file_location('dummy_module', os.path.join(dirname, filename))
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)
                is_module_has_register_attr = getattr(foo, "register", None)
                if is_module_has_register_attr is not None and callable(is_module_has_register_attr):
                    foo.register()

def unregister():
    for dirname, subdirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
        if '__pycache__' in subdirs:
            subdirs.remove('__pycache__')

        for filename in files:
            if filename.endswith('.py') and filename != "__init__.py":
                spec = importlib.util.spec_from_file_location('dummy_module', os.path.join(dirname, filename))
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)
                is_module_has_unregister_attr = getattr(foo, "unregister", None)
                if is_module_has_unregister_attr is not None and callable(is_module_has_unregister_attr):
                    foo.unregister()