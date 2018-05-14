# -*- coding: utf-8 -*-
"""
Runtime for toolchain
"""

from calmjs.runtime import SourcePackageToolchainRuntime
from calmjs.sassy.dist import sourcepath_methods_map
from calmjs.sassy.dist import module_registry_methods
from calmjs.sassy.cli import libsass_toolchain
from calmjs.sassy.cli import create_spec


class ScssRuntime(SourcePackageToolchainRuntime):
    """
    Generic runtime for Scss.
    """

    def __init__(
            self, toolchain, description='calmjs scss bundler tool',
            *a, **kw):
        super(ScssRuntime, self).__init__(
            cli_driver=toolchain, description=description, *a, **kw)

    def init_argparser_export_target(self, argparser):
        super(ScssRuntime, self).init_argparser_export_target(
            argparser,
            help='output filename; defaults to last ${package_name}.css',
        )

    def init_argparser_source_registry(self, argparser):
        # Note that this will set the default destination
        # 'calmjs_module_registry_names', however this only applies
        # within the scope of the argument parsing and that create_spec
        # will use the generic source_registries as the key

        super(ScssRuntime, self).init_argparser_source_registry(
            argparser,
            help=(
                'comma separated list of registries to use for gathering '
                'SCSS sources from the given Python packages; default '
                'behavior is to auto-select, enable verbose output to check '
                'to see which ones were selected'
            ),
        )

    def init_argparser(self, argparser):
        """
        Other runtimes (or users of ArgumentParser) can pass their
        subparser into here to collect the arguments here for a
        subcommand.
        """

        super(ScssRuntime, self).init_argparser(argparser)

        argparser.add_argument(
            '--sourcepath-method', default='all',
            dest='sourcepath_method',
            choices=sorted(sourcepath_methods_map.keys()),
            help='the acquisition method for getting the source module to '
                 'filesystem path mappings from the source registry for the '
                 'given packages; default: all',
        )

        argparser.add_argument(
            '--source-registry-method', default='all',
            dest='source_registry_method',
            choices=sorted(module_registry_methods.keys()),
            help='the acquisition method for getting the list of source '
                 'registries to use for the given packages; default: all',
        )

    def create_spec(
            self, source_package_names=(), export_target=None,
            working_dir=None,
            build_dir=None,
            calmjs_module_registry_names=None,
            source_registry_method='all',
            sourcepath_method='all', bundlepath_method='all',
            toolchain=None, **kwargs):
        """
        Accept all arguments, but also the explicit set of arguments
        that get passed down onto the toolchain.
        """

        # the spec takes a different set of keys as it will ultimately
        # derive the final values for the standardized spec keys.
        return create_spec(
            package_names=source_package_names,
            export_target=export_target,
            working_dir=working_dir,
            build_dir=build_dir,
            source_registry_method=source_registry_method,
            source_registries=calmjs_module_registry_names,
            sourcepath_method=sourcepath_method,
        )


libsass_runtime = ScssRuntime(libsass_toolchain)
