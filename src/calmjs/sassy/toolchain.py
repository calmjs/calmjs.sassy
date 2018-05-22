# -*- coding: utf-8 -*-
"""
Toolchain for building Sassy CSS into CSS.
"""

from __future__ import unicode_literals

import logging
from os.path import join

try:
    import sass
except ImportError:  # pragma: no cover
    HAS_LIBSASS = False
    LIBSASS_VALID_OUTPUT_STYLES = []
else:  # pragma: no cover
    HAS_LIBSASS = True
    LIBSASS_VALID_OUTPUT_STYLES = sorted(sass.OUTPUT_STYLES)

from calmjs.toolchain import Toolchain
from calmjs.toolchain import null_transpiler
from calmjs.toolchain import BUILD_DIR
from calmjs.toolchain import EXPORT_TARGET
from calmjs.toolchain import EXPORT_MODULE_NAMES

from calmjs.sassy.exc import CalmjsSassyRuntimeError

logger = logging.getLogger(__name__)

# spec keys
# the entry points to make use of for the current execution run through
# a calmjs.sassy toolchain.
CALMJS_SASSY_ENTRY_POINTS = 'calmjs_sassy_entry_points'
# the location of the generated sourcefile that will reference the entry
# points specified
CALMJS_SASSY_ENTRY_POINT_SOURCEFILE = 'calmjs_sassy_entry_point_sourcefile'
# the entry point name, typically this will be `index`
CALMJS_SASSY_ENTRY_POINT_NAME = 'calmjs_sassy_entry_point_name'
# key for storing mapping of all the provided sourcepaths, for use with
# providing a control way of stubbing out imports.
CALMJS_SASSY_SOURCEPATH_MERGED = 'calmjs_sassy_sourcepath_merged'
# the importers for libsass.
LIBSASS_IMPORTERS = 'libsass_importers'
# libsass output_style
LIBSASS_OUTPUT_STYLE = 'libsass_output_style'

# definitions
CALMJS_SASSY_ENTRY = 'calmjs.sassy'
LIBSASS_OUTPUT_STYLE_DEFAULT = 'nested'


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

    def assemble(self, spec):
        """
        Since only thing need to be done was to bring the SCSS file into
        the build directory, there should be no further configuration
        files that need to be assembled.  However, linker (the SCSS
        compiler) specific tokens/rules that specifies which "index" or
        entry point to the styles should be specified here.
        """

        spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE] = join(
            spec[BUILD_DIR], spec.get(
                CALMJS_SASSY_ENTRY_POINT_NAME, CALMJS_SASSY_ENTRY
            )
        ) + self.filename_suffix

        # writing out this as a file to permit reuse by other tools that
        # work directly with files.
        with open(spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE], 'w') as fd:
            for modname in spec[CALMJS_SASSY_ENTRY_POINTS]:
                fd.write('@import "%s";\n' % modname)
        logger.debug(
            "wrote entry point module that will import from the following: %s",
            spec[CALMJS_SASSY_ENTRY_POINTS])


class LibsassToolchain(BaseScssToolchain):
    """
    The libsass toolchain.
    """

    def prepare(self, spec):
        """
        Simply check if the libsass package is available, as it is
        required for this toolchain.
        """

        if not HAS_LIBSASS:
            raise CalmjsSassyRuntimeError("missing required package 'libsass'")

    def link(self, spec):
        """
        Use the builtin libsass bindings for the final linking.
        """

        # Loading the entry point from the filesystem rather than
        # tracking through the spec is to permit more transparency for
        # extension and debugging through the serialized form, also to
        # permit alternative integration with tools that read from a
        # file.
        with open(spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE]) as fd:
            source = fd.read()

        logger.info(
            "invoking 'sass.compile' on entry point module at %r",
            spec[BUILD_DIR])
        try:
            css_export = sass.compile(
                string=source,
                importers=spec.get(LIBSASS_IMPORTERS, ()),
                include_paths=[spec[BUILD_DIR]],
                output_style=spec.get(
                    LIBSASS_OUTPUT_STYLE, LIBSASS_OUTPUT_STYLE_DEFAULT),
            )
        except ValueError as e:
            # assume this is the case, could/should be sass.CompileError
            # TODO figure out a better way to represent errors
            raise CalmjsSassyRuntimeError(
                'failed to compile with libsass: %s' % e)

        with open(spec[EXPORT_TARGET], 'w') as fd:
            fd.write(css_export)
        logger.info("wrote export css file at '%s'", spec[EXPORT_TARGET])


def libsass_import_stub_generator(spec):
    """
    Could be a standalone function with a partial applied, but because
    Python 2 is broken this pre-wrapped function is needed

    See: <https://bugs.python.org/issue3445>
    """

    def importer(target):
        """
        Attempt to find the relevant import and stub it out.
        """

        if target in spec[EXPORT_MODULE_NAMES]:
            return None

        if target in spec[CALMJS_SASSY_SOURCEPATH_MERGED]:
            return ((target, ''),)

        # only the / separator is handled as this is typically generated and
        # provided by node_modules or other JavaScript based module systems.
        frags = target.split('/')[:-1]
        while frags:
            stub = '/'.join(frags)
            if stub in spec[CALMJS_SASSY_SOURCEPATH_MERGED]:
                logger.info(
                    "generating stub import for '%s'; provided by '%s'",
                    target, stub,
                )
                return ((target, ''),)
            frags.pop()

        return None

    return importer
