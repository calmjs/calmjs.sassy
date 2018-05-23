# -*- coding: utf-8 -*-
"""
Toolchain for building Sassy CSS into CSS.
"""

from __future__ import unicode_literals

import logging
import os
from os.path import exists
from os.path import join
from os.path import dirname

from calmjs.toolchain import Toolchain
from calmjs.toolchain import null_transpiler
from calmjs.toolchain import BUILD_DIR

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

# definitions
CALMJS_SASSY_ENTRY = 'calmjs.sassy'
CALMJS_SASSY_ASSEMBLE_SUBDIR = '__calmjs_sassy__'


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
            spec[BUILD_DIR], CALMJS_SASSY_ASSEMBLE_SUBDIR, spec.get(
                CALMJS_SASSY_ENTRY_POINT_NAME, CALMJS_SASSY_ENTRY
            )
        ) + self.filename_suffix

        if exists(spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE]):
            raise CalmjsSassyRuntimeError(
                "cannot create entry point module at '%s' as it already "
                "exists" % spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE]
            )

        os.makedirs(dirname(spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE]))
        # writing out this as a file to permit reuse by other tools that
        # work directly with files.
        with open(spec[CALMJS_SASSY_ENTRY_POINT_SOURCEFILE], 'w') as fd:
            for modname in spec[CALMJS_SASSY_ENTRY_POINTS]:
                fd.write('@import "%s";\n' % modname)
        logger.debug(
            "wrote entry point module that will import from the following: %s",
            spec[CALMJS_SASSY_ENTRY_POINTS])
