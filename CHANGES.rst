Changelog
=========

1.0.0 (Unreleased)
------------------

- Initial release of the Sassy CSS integration for Calmjs.
- Provide a base ``calmjs.scss`` registry to allow Python packages to
  export ``.scss`` files for their dependants to utilize.
- Provide a base ``calmjs scss`` runtime to interface with the default
  ``libsass-python`` toolchain for the production of ``.css`` artifacts
  for any given Python packages.
- Provide the default artifact generator for the production of ``.css``
  artifacts at ``calmjs.sassy.artifacts:complete_css``, which interfaces
  with the default ``libsass-python`` toolchain.
