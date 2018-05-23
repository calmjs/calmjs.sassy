# -*- coding: utf-8 -*-
"""
Libsass integration module.
"""

import logging
from itertools import chain

from calmjs.toolchain import BUILD_DIR
from calmjs.toolchain import EXPORT_TARGET
from calmjs.toolchain import EXPORT_MODULE_NAMES

from calmjs.sassy.exc import CalmjsSassyRuntimeError
from calmjs.sassy.toolchain import CALMJS_SASSY_ENTRY_POINT_SOURCEFILE
from calmjs.sassy.toolchain import CALMJS_SASSY_SOURCEPATH_MERGED
from calmjs.sassy.toolchain import BaseScssToolchain

try:
    import sass
except ImportError:  # pragma: no cover
    HAS_LIBSASS = False
    LIBSASS_VALID_OUTPUT_STYLES = []
else:  # pragma: no cover
    HAS_LIBSASS = True
    LIBSASS_VALID_OUTPUT_STYLES = sorted(sass.OUTPUT_STYLES)

logger = logging.getLogger(__name__)

# additional toolchain spec keys
# the importers for libsass.
LIBSASS_IMPORTERS = 'libsass_importers'
# libsass output_style
LIBSASS_OUTPUT_STYLE = 'libsass_output_style'

# definitions
LIBSASS_OUTPUT_STYLE_DEFAULT = 'nested'


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


def libsass_spec_extras(
        spec,
        libsass_output_style=LIBSASS_OUTPUT_STYLE_DEFAULT,
        **kw):
    """
    Apply the libsass toolchain specific spec keys
    """

    spec[LIBSASS_OUTPUT_STYLE] = libsass_output_style
    # build the stub importer, if applicable for stubbing out external
    # imports for non-all definitions using the merged mapping
    if spec[CALMJS_SASSY_SOURCEPATH_MERGED]:
        spec[LIBSASS_IMPORTERS] = list(chain(
            spec.get(LIBSASS_IMPORTERS, []),
            [(0, libsass_import_stub_generator(spec))],
        ))
    return spec


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
            spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE])
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
