# -*- coding: utf-8 -*-
"""
Toolchain for building Sassy CSS into CSS.
"""

from __future__ import unicode_literals

try:
    import sass
except ImportError:  # pragma: no cover
    HAS_LIBSASS = False
else:  # pragma: no cover
    HAS_LIBSASS = True

from calmjs.toolchain import Toolchain
from calmjs.toolchain import null_transpiler

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

    def prepare(self, spec):
        """
        Simply check if the libsass was found by this module.
        """

        if not HAS_LIBSASS:
            raise CalmjsSassyRuntimeError('the libsass package is not found.')

    def assemble(self, spec):
        """
        Some kind of assembly will need to be done here
        """


class LibsassToolchain(BaseScssToolchain):
    """
    The libsass toolchain.
    """

    def link(self, spec):
        """
        Use the builtin libsass bindings for the final linking.
        """

        sass.compile
