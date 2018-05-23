# -*- coding: utf-8 -*-
"""
Lower level API for creating linkage with an scss implementation.
"""

from os.path import basename
from os.path import join
from os.path import realpath
import logging

from calmjs.toolchain import Spec

from calmjs.toolchain import BUILD_DIR
from calmjs.toolchain import EXPORT_TARGET
from calmjs.toolchain import SOURCE_PACKAGE_NAMES
from calmjs.toolchain import CALMJS_MODULE_REGISTRY_NAMES
from calmjs.toolchain import WORKING_DIR
from calmjs.toolchain import spec_update_sourcepath_filter_loaderplugins

from calmjs.sassy.toolchain import CALMJS_SASSY_ENTRY_POINT_NAME
from calmjs.sassy.toolchain import CALMJS_SASSY_ENTRY_POINTS
from calmjs.sassy.toolchain import CALMJS_SASSY_SOURCEPATH_MERGED

from calmjs.sassy.dist import generate_scss_sourcepaths
from calmjs.sassy.dist import generate_scss_bundle_sourcepaths
from calmjs.sassy.dist import get_calmjs_scss_module_registry_for

from calmjs.sassy.libsass import libsass_spec_extras
from calmjs.sassy.libsass import LibsassToolchain

logger = logging.getLogger(__name__)

libsass_toolchain = LibsassToolchain()

_implementation_extras = [
    (LibsassToolchain, libsass_spec_extras),
]


def create_spec(
        package_names, export_target=None, working_dir=None, build_dir=None,
        source_registry_method='all', source_registries=None,
        sourcepath_method='all',
        bundlepath_method='all',
        calmjs_sassy_entry_point_name='index',
        calmjs_sassy_entry_points=None,
        toolchain=libsass_toolchain,
        **kw):
    """
    Produce a spec for the compilation through any BaseScssToolchain
    subclasses that have implemented the correct interfaces, with extra
    features and keys generated if a supported implementation was
    provided.

    Arguments:

    package_names
        The name of the Python package to source the dependencies from.

    export_target
        The filename for the output, can be an absolute path to a file.
        Defaults to the package_name with a '.css' suffix added in the
        working_dir.

    working_dir
        The working directory.  If the package specified any extras
        calmjs requirements (e.g. node_modules), they will be searched
        for from here.  Defaults to current working directory.

    build_dir
        The build directory.  Defaults to a temporary directory that is
        automatically removed when done.

    source_registry_method
        The acqusition method for the list of calmjs module registries
        declared for the provided package names.

        'all'
            Traverse the dependency graph for the specified package to
            acquire the declared calmjs module registries to use.
        'explicit'
            Only use the calmjs module registries declared for specified
            packages.
        'none'
            Do not acquire sources.  Useful for creating bundles of just
            the bundle sources.

    source_registries
        If the provided packages did not specify all registries or have
        declared modules in alternative but not explicitly specified
        calmjs module registries, this option can be used to pass an
        explicit list of calmjs module registries to use.  Typical use
        case is to generate tests.

    sourcepath_method
        The acquisition method for the source mapping for the given
        package from the source_registries specified.  Choices are
        between 'all', 'explicit' or 'none'.  Defaults to 'all'.

        'all'
            Traverse the dependency graph for the specified package to
            acquire the sources declared for each of those modules.
        'explicit'
            Only acquire the sources for the specified package.
        'none'
            Do not acquire sources.  Useful for creating bundles of just
            the bundle sources.

    bundlepath_method
        The acquisition method for the bundle sources for the given
        module.  Choices are between 'all', 'explicit' or 'none'.
        Defaults to 'all'.

        'all'
            Traverse the dependency graph for the specified package and
            acquire the declarations.
        'explicit'
            Only acquire the bundle sources declared for the specified
            package.
        'none'
            Do not specify any bundle files.  This only works for
            packages that have declared these as optional

        Defaults to 'all'.

    calmjs_sassy_entry_point_name
        The name for the main entry point.  This is the module name that
        will be searched for in each of the modules.

        Defaults to 'index'.

    calmjs_sassy_entry_points
        The scss module names that will be used as the entry points to
        link the scss rules provided in the build directory.  If None
        are provided, a entry_point_filename will be derived from the
        calmjs_sassy_entry_point_name and the toolchain.filename_suffix
        which will then be used to source the entry points from the
        provided packages specified by package_name

    toolchain
        The Toolchain class this spec is targetted for.  Default to the
        default libsass_toolchain instance.  Note that attributes
        provided by this instance will be used for certain default
        parameters.

        filename_suffix
            Will be joined with calmjs_sassy_entry_point_name to
            acquire the file name for the entry point, if the specific
            entry points are not provided by calmjs_sassy_entry_points.
        join_cwd
            Function will be called to acquire the working directory,
            if working_dir is not provided.

    """

    working_dir = working_dir if working_dir else toolchain.join_cwd()

    if export_target is None:
        # Take the final package name for now...
        if package_names:
            export_target = realpath(
                join(working_dir, package_names[-1] + '.css'))
        else:
            export_target = realpath(
                join(working_dir, 'calmjs.sassy.export.css'))

    spec = Spec()

    if source_registries is None:
        source_registries = get_calmjs_scss_module_registry_for(
            package_names, method=source_registry_method)
        if source_registries:
            logger.info(
                "automatically picked registries %r for sourcepaths",
                source_registries,
            )
        elif package_names:
            # TODO figure out if defaulting to calmjs.scss is better
            logger.warning(
                "no module registry declarations found using packages %r "
                "with acquisition method '%s'",
                package_names, source_registry_method,
            )
        else:
            logger.warning(
                'no packages and registries specified for spec construction')
    else:
        logger.info(
            "using manually specified registries %r for sourcepaths",
            source_registries,
        )

    spec[BUILD_DIR] = build_dir
    spec[CALMJS_MODULE_REGISTRY_NAMES] = source_registries
    spec[CALMJS_SASSY_ENTRY_POINT_NAME] = calmjs_sassy_entry_point_name
    spec[EXPORT_TARGET] = export_target
    spec[SOURCE_PACKAGE_NAMES] = package_names
    spec[WORKING_DIR] = working_dir

    spec_update_sourcepath_filter_loaderplugins(
        spec, generate_scss_sourcepaths(
            package_names=package_names,
            registries=source_registries,
            method=sourcepath_method,
        ), 'transpile_sourcepath')

    spec_update_sourcepath_filter_loaderplugins(
        spec, generate_scss_bundle_sourcepaths(
            package_names=package_names,
            working_dir=working_dir,
            method=bundlepath_method,
        ), 'bundle_sourcepath')

    # need one that merges all sources for sourcepaths to declare all
    # the available paths to stub just the provided sources.
    spec[CALMJS_SASSY_SOURCEPATH_MERGED] = {}
    if sourcepath_method != 'all':
        spec[CALMJS_SASSY_SOURCEPATH_MERGED].update(generate_scss_sourcepaths(
            package_names=package_names,
            registries=source_registries,
            method='all',
        ))
    if bundlepath_method != 'all':
        spec[
            CALMJS_SASSY_SOURCEPATH_MERGED
        ].update(generate_scss_bundle_sourcepaths(
            package_names=package_names,
            working_dir=working_dir,
            method='all',
        ))

    if calmjs_sassy_entry_points:
        spec[CALMJS_SASSY_ENTRY_POINTS] = calmjs_sassy_entry_points
        logger.debug(
            "using provided targets %r as entry points for css "
            "generation", calmjs_sassy_entry_points,
        )
    else:
        # There duplicates the above call, but this is done to avoid
        # making any assumptions about what module name formats are
        # being used.  The goal is to find the entry point from the
        # provided packages.
        entry_point_filename = (
            calmjs_sassy_entry_point_name + toolchain.filename_suffix)
        spec[CALMJS_SASSY_ENTRY_POINTS] = [
            modname for modname, sourcepath in generate_scss_sourcepaths(
                package_names=package_names,
                registries=source_registries,
                method='explicit',
            ).items() if basename(sourcepath) == entry_point_filename
        ]
        logger.debug(
            "using derived '%s' targets %r as entry points for css generation",
            toolchain.filename_suffix, spec[CALMJS_SASSY_ENTRY_POINTS],
        )

    for cls, f in _implementation_extras:
        if isinstance(toolchain, cls):
            f(spec, **kw)

    return spec


def compile_all(
        package_names, export_target=None, working_dir=None, build_dir=None,
        source_registry_method='all', source_registries=None,
        sourcepath_method='all', bundlepath_method='all',
        calmjs_sassy_entry_point_name='index',
        calmjs_sassy_entry_points=None,
        toolchain=libsass_toolchain,
        **kw):
    """
    Invoke the scss compilation through the provided toolchain class to
    generate a CSS file containing all the styling rules defined by the
    provided Python package(s).

    Arguments:

    toolchain
        The toolchain instance to use.  Default is an instance of the
        libsass toolchain.

    For other arguments, please refer to create_spec as they are passed
    to it.

    Naturally, if any Node.js dependancies have been declared they will
    need to be made available before the compilation is successful.
    """

    spec = create_spec(
        package_names=package_names,
        export_target=export_target,
        working_dir=working_dir,
        build_dir=build_dir,
        source_registry_method=source_registry_method,
        source_registries=source_registries,
        sourcepath_method=sourcepath_method,
        bundlepath_method=bundlepath_method,
        calmjs_sassy_entry_point_name=calmjs_sassy_entry_point_name,
        calmjs_sassy_entry_points=calmjs_sassy_entry_points,
        toolchain=toolchain,
        **kw
    )
    toolchain(spec)
    return spec
