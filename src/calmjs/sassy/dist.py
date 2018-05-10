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

import logging
from os.path import join
from os.path import isdir
from calmjs.registry import get
from calmjs import dist

logger = logging.getLogger(__name__)


def map_none(*a, **kw):
    return {}


CALMJS_SCSS_MODULE_REGISTRY_FIELD = 'calmjs_scss_module_registry'
CALMJS_SCSS_REGISTRY = 'calmjs.scss'
EXTRAS_CALMJS_SCSS_FIELD = 'extras_calmjs_scss'

(get_extras_calmjs_scss, flatten_extras_calmjs_scss,
    flatten_parents_extras_calmjs_scss, write_extras_calmjs_scss) = (
        dist.build_helpers_egginfo_json(
            EXTRAS_CALMJS_SCSS_FIELD, dist.JSON_EXTRAS_REGISTRY_KEY))

(get_module_registry_names, flatten_module_registry_names,
    write_module_registry_names) = dist.build_helpers_module_registry_name(
        CALMJS_SCSS_MODULE_REGISTRY_FIELD)

(get_module_registry_dependencies, flatten_module_registry_dependencies,
    flatten_parents_module_registry_dependencies) = (
        dist.build_helpers_module_registry_dependencies(
            registry_name=CALMJS_SCSS_REGISTRY))

module_registry_methods = {
    'all': flatten_module_registry_names,
    'explicit': get_module_registry_names,
}

sourcepath_methods_map = {
    'all': flatten_module_registry_dependencies,
    'explicit': get_module_registry_dependencies,
    'none': map_none,
}

bundle_sourcepath_methods_map = {
    'all': flatten_extras_calmjs_scss,
    'explicit': get_extras_calmjs_scss,
    'none': map_none,
}


def get_calmjs_scss_module_registry_for(package_names, method='all'):
    """
    Acquire the dedicated SCSS registries declared by packages.

    Arguments:

    package_names
        List of package names
    method
        Either across all dependencies of the packages or explicit on
        the list of provided packages.  Defaults to 'all', alternatively
        'explicit' is an accepted value.
    """

    return module_registry_methods.get(
        method, flatten_module_registry_names)(package_names)


def generate_scss_sourcepaths(
        package_names, registries=('calmjs.scss',), method='all'):
    """
    Acquire the sourcepath from the packages using the registries and
    method provided.

    Arguments:

    package_names
        List of package names to be used for source acquisition
    registries
        Registries to use
    method
        Either across all dependencies of the packages or explicit on
        the list of provided packages.  Defaults to 'all', alternatively
        'explicit' is an accepted value.
    """

    sourcepaths = {}
    for registry_name in registries:
        sourcepaths.update(sourcepath_methods_map.get(
            method, flatten_module_registry_dependencies)(
                package_names, registry_name=registry_name))
    return sourcepaths


def generate_scss_bundle_sourcepaths(
        package_names, working_dir, method='all',
        extras_key=dist.JSON_EXTRAS_REGISTRY_KEY):
    """
    Acquire the bundled soucepaths defined by the packages using the
    working directory and the method provided.

    Arguments:

    package_names
        List of package names to be used for source acquisition
    working_dir
        The working directory to find the bundled sources.
    method
        Either across all dependencies of the packages or explicit on
        the list of provided packages.  Defaults to 'all', alternatively
        'explicit' and 'none' is an accepted value, for explicitly only
        using declarations by the provided packages or not at all.
    """

    # the extras keys will be treated as valid Node.js package manager
    # subdirectories.
    valid_pkgmgr_dirs = set(get(extras_key).iter_records())
    extras_calmjs_scss = bundle_sourcepath_methods_map.get(
        method, flatten_extras_calmjs_scss)(package_names)
    bundle_sourcepaths = {}

    for mgr in extras_calmjs_scss:
        if mgr not in valid_pkgmgr_dirs:
            continue
        basedir = join(working_dir, mgr)
        if not isdir(basedir):
            if extras_calmjs_scss[mgr]:
                logger.warning(
                    "acquired extras_calmjs_scss needs from '%s', but working "
                    "directory '%s' does not contain it; bundling may fail.",
                    mgr, working_dir
                )
            continue  # pragma: no cover

        for k, v in extras_calmjs_scss[mgr].items():
            bundle_sourcepaths[k] = join(basedir, *(v.split('/')))

    return bundle_sourcepaths
