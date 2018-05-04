# -*- coding: utf-8 -*-
"""
Registry for SCSS files.
"""

from functools import partial
from calmjs.indexer import mapper
from calmjs.module import ModuleRegistry


class SCSSRegistry(ModuleRegistry):

    def _init(self):
        self.mapper = partial(mapper, fext='.scss')
