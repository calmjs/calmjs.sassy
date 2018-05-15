# -*- coding: utf-8 -*-
"""
CalmJS css artifact generation helpers
"""

from calmjs.sassy.cli import create_spec
from calmjs.sassy.cli import libsass_toolchain


def complete_css(package_names, export_target):
    """
    Return the toolchain and a spec that when executed together, will
    result in a complete artifact using the provided package names onto
    the export_target.
    """

    return libsass_toolchain, create_spec(package_names, export_target)
