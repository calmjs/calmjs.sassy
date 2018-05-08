# -*- coding: utf-8 -*-
"""
Integration with distribution management.

Note that this module essentially defines a new keyword specifically for
the tracking of SCSS sources.  The reason why this is not using the
default calmjs.modules and calmjs_module_registry field is due to how
this tool is unlikely to interact with any JavaScript/Node.js specific
items, and not because the reverse is not true.  In fact, if dependent
packages wish to include the CSS generation as part of their JavaScript
workflow, the appropriate registry can be declared directly on the
calmjs_module_registry field for that given package and the calmjs
integrated Node.js tooling should be able to pick those up.
"""

from calmjs import dist

CALMJS_SCSS_MODULE_REGISTRY_FIELD = 'calmjs_scss_module_registry'

(get_module_registry_names, flatten_module_registry_names,
    write_module_registry_names) = dist.build_helpers_module_registry_name(
        CALMJS_SCSS_MODULE_REGISTRY_FIELD)

module_registry_methods = {
    'all': flatten_module_registry_names,
    'explicit': get_module_registry_names,
}


def get_calmjs_scss_module_registry_for(package_names, method='all'):
    return module_registry_methods.get(
        method, flatten_module_registry_names)(package_names)
