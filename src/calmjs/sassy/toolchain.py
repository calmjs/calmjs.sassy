# -*- coding: utf-8 -*-
"""
Toolchain for building Sassy CSS into CSS.
"""

from __future__ import unicode_literals

from os.path import join

try:
    import sass
except ImportError:  # pragma: no cover
    HAS_LIBSASS = False
else:  # pragma: no cover
    HAS_LIBSASS = True

from calmjs.toolchain import Toolchain
from calmjs.toolchain import null_transpiler
from calmjs.toolchain import BUILD_DIR
from calmjs.toolchain import EXPORT_TARGET

from calmjs.sassy.exc import CalmjsSassyRuntimeError

# spec keys
CALMJS_SCSS_MODULE_REGISTRY_NAMES = 'calmjs_scss_module_registry_names'
CALMJS_SCSS_ENTRY_POINTS = 'calmjs_scss_entry_points'
CALMJS_SCSS_ENTRY_POINT_SOURCE = 'calmjs_scss_entry_point_source'

# definitions
CALMJS_SCSS_ENTRY_POINT_NAME = 'calmjs.sassy.scss'


class BaseScssToolchain(Toolchain):
    """
    The base SCSS Toolchain.
    """

    def setup_transpiler(self):
        self.transpiler = null_transpiler

    def setup_filename_suffix(self):
        """
        Since this toolchain is specifically for .scss files.
        """

        self.filename_suffix = '.scss'

    def transpile_modname_source_target(self, spec, modname, source, target):
        """
        Calls the original version.
        """

        # XXX should just simply copy the files for now.
        return self.simple_transpile_modname_source_target(
            spec, modname, source, target)

    def prepare(self, spec):
        """
        Simply check if the libsass was found by this module.
        """

        if not HAS_LIBSASS:
            raise CalmjsSassyRuntimeError('the libsass package is not found.')

    def assemble(self, spec):
        """
        Since only thing need to be done was to bring the SCSS file into
        the build directory, there should be no further configuration
        files that need to be assembled.  However, linker (the SCSS
        compiler) specific tokens/rules that specifies which "index" or
        entry point to the styles should be specified here.
        """

        spec[CALMJS_SCSS_ENTRY_POINT_SOURCE] = join(
            spec[BUILD_DIR], CALMJS_SCSS_ENTRY_POINT_NAME)

        # writing out this as a file to permit reuse by other tools that
        # work directly with files.
        with open(spec[CALMJS_SCSS_ENTRY_POINT_SOURCE], 'w') as fd:
            for modname in spec[CALMJS_SCSS_ENTRY_POINTS]:
                fd.write('@import "%s";\n' % modname)


class LibsassToolchain(BaseScssToolchain):
    """
    The libsass toolchain.
    """

    def link(self, spec):
        """
        Use the builtin libsass bindings for the final linking.
        """

        # Loading the entry point from the filesystem rather than
        # tracking through the spec is to permit more transparency for
        # extension and debugging through the serialized form, also to
        # permit alternative integration with tools that read from a
        # file.
        with open(spec[CALMJS_SCSS_ENTRY_POINT_SOURCE]) as fd:
            source = fd.read()

        try:
            css_export = sass.compile(
                string=source, include_paths=[spec[BUILD_DIR]])
        except ValueError:
            # assume this is the case, could/should be sass.CompileError
            # TODO figure out a better way to represent errors
            raise CalmjsSassyRuntimeError('failed to compile with libsass')

        with open(spec[EXPORT_TARGET], 'w') as fd:
            fd.write(css_export)
