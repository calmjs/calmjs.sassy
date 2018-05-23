Changelog
=========

1.0.1 (2018-05-23)
------------------

- Minor text fixes.

1.0.0 (2018-05-23)
------------------

- Initial release of the Sassy CSS integration for Calmjs.
- Provide a base ``calmjs.scss`` registry to allow Python packages to
  export ``.scss`` files for their dependants to utilize.
- Provide a base ``calmjs scss`` runtime to interface with the default
  ``libsass-python`` toolchain for the production of ``.css`` artifacts
  for any given Python packages.
- Provide a couple artifact builders that integrates with the calmjs
  artifact production framework.
