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
else:  # pragma: no cover
    HAS_LIBSASS = True

from calmjs.toolchain import Toolchain
from calmjs.toolchain import null_transpiler
from calmjs.toolchain import BUILD_DIR
from calmjs.toolchain import EXPORT_TARGET
from calmjs.toolchain import EXPORT_MODULE_NAMES

from calmjs.sassy.exc import CalmjsSassyRuntimeError

logger = logging.getLogger(__name__)

# spec keys
CALMJS_SCSS_MODULE_REGISTRY_NAMES = 'calmjs_scss_module_registry_names'
CALMJS_SCSS_ENTRY_POINTS = 'calmjs_scss_entry_points'
CALMJS_SCSS_ENTRY_POINT_SOURCE = 'calmjs_scss_entry_point_source'
CALMJS_LIBSASS_IMPORTERS = 'calmjs_libsass_importers'
SOURCEPATH_MERGED = 'sourcepath_merged'

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
        logger.debug(
            "wrote entry point module that will import from the following: %s",
            spec[CALMJS_SCSS_ENTRY_POINTS])


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

        logger.info(
            "invoking 'sass.compile' on entry point module at %r",
            spec[BUILD_DIR])
        try:
            css_export = sass.compile(
                string=source,
                importers=spec.get(CALMJS_LIBSASS_IMPORTERS, ()),
                include_paths=[spec[BUILD_DIR]],
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

        if target in spec[SOURCEPATH_MERGED]:
            return ((target, ''),)

        # only the / separator is handled as this is typically generated and
        # provided by node_modules or other JavaScript based module systems.
        frags = target.split('/')[:-1]
        while frags:
            stub = '/'.join(frags)
            if stub in spec[SOURCEPATH_MERGED]:
                logger.info(
                    "generating stub import for '%s'; provided by '%s'",
                    target, stub,
                )
                return ((target, ''),)
            frags.pop()

        return None

    return importer
