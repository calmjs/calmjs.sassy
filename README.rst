calmjs.sassy
============

Package for extending the `Calmjs framework`_ to support the declaration
and usage of |sass|_ in a manner that crosses Python package boundaries
by exposing an ``import`` system that mimics the package namespaces
available within the current Python environment, such that styling rules
can be more easily propagated to their dependants.  This facilitates the
reuse of styling rules declared by Python packages' dependencies in a
manner more familiar to users of the given Python environments by
reusing the same names as the namespaces they may be using.

.. image:: https://travis-ci.org/calmjs/calmjs.sassy.svg?branch=1.0.0
    :target: https://travis-ci.org/calmjs/calmjs.sassy
.. image:: https://ci.appveyor.com/api/projects/status/1gei512socwe8nho/branch/1.0.0?svg=true
    :target: https://ci.appveyor.com/project/metatoaster/calmjs-sassy/branch/1.0.0
.. image:: https://coveralls.io/repos/github/calmjs/calmjs.sassy/badge.svg?branch=1.0.0
    :target: https://coveralls.io/github/calmjs/calmjs.sassy?branch=1.0.0

.. |calmjs| replace:: ``calmjs``
.. |calmjs.rjs| replace:: ``calmjs.rjs``
.. |calmjs.sassy| replace:: ``calmjs.sassy``
.. |calmjs.webpack| replace:: ``calmjs.webpack``
.. |libsass-python| replace:: ``libsass-python``
.. |npm| replace:: ``npm``
.. |sass| replace:: ``sass``
.. _Calmjs framework: https://pypi.python.org/pypi/calmjs
.. _calmjs: https://pypi.python.org/pypi/calmjs
.. _calmjs.rjs: https://pypi.python.org/pypi/calmjs.rjs
.. _calmjs.webpack: https://pypi.python.org/pypi/calmjs.webpack
.. _libsass-python: https://sass.github.io/libsass-python/
.. _npm: https://www.npmjs.com/
.. _sass: https://sass-lang.com/

Introduction
------------

While the |calmjs|_ framework can support the production of deployable
artifacts for web applications (through packages such as |calmjs.rjs|_
and |calmjs.webpack|_), the styling of the application would be
incomplete without exposing the relevant stylesheets to dependant
packages.

With the usage of the extensibility of the calmjs framework, a registry
dedicated for |sass| may be declared.  Tools that make use of these
declarations may also be integrated to generate a single (or a set of)
stylesheets for use with the library or the application.


Features
--------

This package provides:

- A base registry that finds all ``.scss`` files declared in a Python
  package.
- A basic toolchain for linking all the ``.scss`` files exported by a
  given Python package(s) and their dependencies, plus optionally their
  Node.js/npm dependencies discovered through the dependency graph with
  the aid of |calmjs|_, for the generation of ``.css`` files for use by
  the application or export to other libraries.  A specific
  implementation that links against |libsass-python|_ is provided.
- A calmjs runtime that makes use of the |libsass-python| toolchain for
  end-user one-off CSS generation.


Installation
------------

To install |calmjs.sassy| into a given Python environment, the base
package may be installed directly from PyPI with the following command:

.. code:: sh

    $ pip install calmjs.sassy

If support for the usage of |libsass-python| is desired, the
installation command will be the following:

.. code:: sh

    $ pip install calmjs.sassy[libsass]

If this package is used as part of the build process, and the default
|libsass-python| toolchain is used for CSS artifact generation, the
dependency may be declared like so in the package's ``setup.py`` file:

.. code:: python

    setup(
        ...
        setup_requires=[
            'calmjs.sassy>=1.0.0,<2',
            # plus other packages required for generating the package.
        ],
        install_requires=[
            # actual dependencies required for the usage of the package.
        ],
    )

Alternative installation methods (advanced users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Development is still ongoing with |calmjs.sassy|; the development
version may be installed through git like so:

.. code:: sh

    $ pip install calmjs
    $ pip install git+https://github.com/calmjs/calmjs.sassy.git#egg=calmjs.sassy

Alternatively, the git repository can be cloned directly and execute
``pip install -e .`` while inside the root of the source directory.

Newer versions of ``pip`` and ``setuptools`` may omit the initial manual
installation of the |calmjs| package.

If ``setup.py`` within the |calmjs.sassy| source tree is used directly,
please keep in mind that |calmjs| MUST be available before that is
executed, so that all the required package metadata may be generated
correctly.  Alternatively, please execute ``python setup.py egg_info``
if any message about ``Unknown distribution option:`` is noted during
the invocation of ``setup.py``.

As |calmjs| is declared as both namespace and package, there are certain
low-level setup that is required on the working Python environment to
ensure that all modules within can be located correctly.  However,
versions of ``setuptools`` earlier than `v31.0.0`__ does not create the
required package namespace declarations when a package is installed
using this development installation method when mixed with ``pip
install`` within the same namespace.  As a result, inconsistent import
failures can happen for any modules under the |calmjs| namespace.  As an
example:

.. __: https://setuptools.readthedocs.io/en/latest/history.html#v31-0-0

.. code:: python

    >>> import calmjs.sassy
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ImportError: No module named 'calmjs.sassy'
    >>> import calmjs.base
    >>> import calmjs.sassy
    >>>

If this behavior (and workaround) is undesirable, please ensure the
installation of all |calmjs| related packages follow the same method
(i.e. either ``python setup.py develop`` for all packages, or using the
wheels acquired through ``pip``), or upgrade ``setuptools`` to version
31 or greater and reinstall all affected packages.

Testing the installation
~~~~~~~~~~~~~~~~~~~~~~~~

Finally, to verify for the successful installation of |calmjs.sassy|,
the included tests may be executed through this command:

.. code:: sh

    $ python -m unittest calmjs.sassy.tests.make_suite


Usage
-----

To generate the ``.css`` artifact for given package(s) that have
exported ``.scss`` styles through the Calmjs module registry system, and
that the package |libsass-python| is available, the following command
may be executed:

.. code:: sh

    $ calmjs scss example.package

The following sections will provide an overview on how this export
system may be enabled for Python packages.  For a more detailed
explanation on how the module registry works or how Calmjs works in
general, please refer to the README provided by the |calmjs|_ package,
under the section `Export JavaScript code from Python packages`__.

.. __: https://pypi.python.org/pypi/calmjs/#export-javascript-code-from-python-packages

The default runtime also exposes a number of tuneable features as flags
that are documented below; the specifics may be found by running
``calmjs scss --help``.

Declaring SCSS files to export for a given Python package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SCSS files embedded within a Python package can be exposed to the
``calmjs.scss`` registry which is provided by this package.  For
example, given the the following entry points for that registry defined
by a package named ``example``:

.. code:: ini

    [calmjs.scss]
    example = example

This is the most basic declaration that works for packages that share
the same name as the import location provided.

The following is am example for packages that have nested submodules
(called ``example.lib`` and ``example.app``):

.. code:: ini

    [calmjs.scss]
    example.lib = example.lib
    example.app = example.app

While the import locations declared looks exactly like a Python module
(as per the rules of a Python entry point), the ``calmjs.scss``
registry will present them using the CommonJS/ES6 style import paths
(i.e.  ``'example/lib'`` and ``'example/app'``), so users that need
those style rules need to be ensure that they ``import`` those strings.

Please also note that the default source extractor will extract all
``*.scss`` files within those directories.

Putting the second example together, the ``setup.py`` file should
contain the following:

.. code:: Python

    setup(
        name='example',
        setup_requires=[
            'calmjs.scss',
            # plus other setup level requirements
        ],
        # the entry points are required to allow calmjs to pick this up
        entry_points="""
        [calmjs.scss]
        example.lib = example.lib
        example.app = example.app
        """,
    )

Ensure the SCSS is structured in the supported manner for reuse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For proper generation of the resulting ``.css`` and the management of
the ``.scss`` usage and exports, the default |libsass-python| toolchain
imposes a small number of fixed constraints when default settings are
used.  The main constraint is that a specific entry point file must be
declared to be used to acquire the styling rules for the specified
packages for the generation of the stylesheet artifact(s).  This
parameter typically defaults to ``index.scss``, but this may be
specified to a different value to generate different styling rules, for
example for usage with different application end points.

In essence, this allow the package to create an artifact with just the
explicit imports and styling rules defined within it, while exporting
the rules it defines to their dependants piecemeal so that they may be
able to import them using the similar package namespace and module
names.  This enables general communication of exports and reusability of
those styling rules without forcing dependants to explicitly declare
their required styles multiple times (i.e. only the ``@import``
statement is needed in the stylesheet itself, and no need to declare
an explicit entry against something outside the package).

For example, inside an ``example.package`` there may be this layout::

    .
    ├── example
    │   ├── __init__.py
    │   └── package
    │       ├── __init__.py
    │       ├── colors.scss
    │       ├── content.py
    │       ├── form.py
    │       ├── form.scss
    │       ├── index.scss
    │       ├── ui.py
    │       ├── ui.scss
    │       └── widget.js
    └── setup.py

The entry point declaration to export the ``.scss`` files within the
example package will be this:

.. code:: ini

    [calmjs.scss]
    example.package = example.package

Note that the ``index.scss`` (the default entry point name) for this
package may contain the following:

.. code:: css

    @import "example/package/colors";
    @import "example/package/form";
    @import "example/package/ui";

Which are simply imports of all the ``.scss`` modules provided by the
package itself.  For an ``example.dependant`` package that depends on
``example.package`` and exports their own styling rules, it will need
to declare its dependency through the ``install_requires`` keyword in
its ``setup.py`` and declare the following entry point to expose the
styles defined:

.. code:: ini

    [calmjs.scss]
    example.dependant = example.dependant

Putting it all together:

.. code:: python

    setup(
        name='example.dependant',
        install_requires=[
            'example.package',
            # ... plus other dependencies
        ],
        entry_points="""
        [calmjs.scss]
        example.dependant = example.dependant
        """,
        # ... plus other declarations
    )

Note that the entry specific to its dependency ``example.package`` is
already declared already by that package.  For the main entry point
``index.scss`` of ``example.dependant``, it may contain the following:

.. code:: css

    @import "example/dependant/colors";
    @import "example/dependant/full_ui";
    @import "example/package/form";

In this example, only the ``form.scss`` styles exported by the
``example.package`` was included, while omitting ``colors.scss`` and
``ui.scss`` as it could clash with the definitions required and
implemented by the other styles it shipped in that dependant package
(e.g. ``colors`` and ``full_ui``).  Other dependants of this
``example.dependant`` package may then declare usage of any of these
exported styles as per their owners' preferences.  This is one method to
provide extensible styles that are reusable in a piecemeal manner by
package dependants.

Naturally, there are parameters to specify entry points other than
``index.scss`` for a given package, if necessary (for example, multiple
stylesheets may need to be exported for use with different workflows
provided by the given package).

Include .scss files in Node.js package repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As the integration with Node.js was the goal of the Calmjs framework, it
is possible to declare linkage with Node.js packages that ship with
``.scss`` files from package repositories such as |npm|_.  The actual
usage is very similar to the typical integration through Calmjs, where
the difference lies in the keywords to be specified.

For example, a ``setup.py`` may contain the following:

.. code:: Python

    setup(
        name="example.package"
        package_json={
            "dependencies": {
                "bootstrap": "~4.0.0",
            },
        },
        extras_calmjs_scss={
            'node_modules': {
                'bootstrap': 'bootstrap/scss',
            }
        },
    )

The declaration above with simply expose all the ``.scss`` files inside
the ``bootstrap`` package from ``npm`` as the directory was declared to
be used for the build process.  Importing the desired module from that
dependency is simply:

.. code:: css

    @import "bootstrap/nav";
    @import "bootstrap/navbar";

Would work seamlessly, much like the usage of JavaScript code.

Complete artifacts from ``npm`` may also be explicitly specified to
export under a specific identifier.

Declaring prebuilt, standard CSS bundle for the Python package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, to complete the Python package deployment story, the process
should include the automatic generation and inclusion of the stylesheet
artifacts in the resulting Python wheel.  This can be achieved by
specifying an entry in the ``calmjs.artifacts`` registry, with the key
being the filename of the artifact and the value being the import
location to a builder.  A default builder function provided at
``calmjs.sassy.artifact:complete_css`` will enable the generation
of a complete stylesheet, based on the default toolchain and settings,
with ``calmjs.sassy.artifact:complete_compressed_css`` provide a spec
that will produced compressed style output.  Note that both these
builders make use of the ``libsass-python`` toolchain.

An example entry point configuration that only produce the complete css
artifact (without compression):

.. code:: ini

    [calmjs.artifacts]
    example.bundle.css = calmjs.sassy.artifact:complete_css

Once those entry points are installed, running ``calmjs artifact build
example.package`` will make use of the SCSS toolchain and build the
artifact at ``example.bundle.css`` inside the ``calmjs_artifacts``
directory within the metadata directory for ``example.package``.
Alternatively, for solution more integrated with ``setuptools``, the
``setup`` function in ``setup.py`` should also enable the
``build_calmjs_artifacts`` flag such that ``setup.py build`` will also
trigger the building process.  This is useful for automatically
generating and including the artifact as part of the wheel building
process.

A more complete definition that generates both form of the artifacts may
look like the following ``setup.py``:

.. code:: Python

    setup(
        name='example.package',
        # to enable calmjs artifact generation integration w/ setuptools
        build_calmjs_artifacts=True,
        entry_points="""
        # ... other entry points truncated
        [calmjs.module]
        example.package = example.package

        [calmjs.artifacts]
        example.bundle.css = calmjs.sassy.artifact:complete_css
        example.bundle.min.css = calmjs.sassy.artifact:complete_compressed_css
        """,
        # ... other required fields truncated
    )

Building the wheel using ``setup.py`` may result in something like this.

.. code::

    $ python setup.py bdist_wheel
    automatically picked registries ['calmjs.scss'] for sourcepaths
    ...
    invoking 'sass.compile' on entry point module at '/tmp/tmpwb5bhmd0/build/__calmjs_sassy__/index.scss'
    wrote export css file at '/home/user/example.package/src/example.package.egg-info/calmjs_artifacts/example.bundle.css'
    installing to build/bdist.linux-x86_64/wheel
    ...

With both ``example.bundle.css`` and ``example.bundle.min.css``
available under the ``calmjs_artifacts`` sub-directory inside the
package metadata directory inside the Python wheel that was generated.

Also note that the default builder specifies ``index`` as the default
entry point.  If other ones need to be provided or other options are
required, simply create a new builder function that return a ``Spec``
object with the desired values.

The end result is that end-users of this package will be able to make
use of the complete features provided without having to go through a
separate build step, while retaining the ability for regenerating all
the required artifacts with just the build dependencies installed,
without having to further acquire the original configuration files (or
even the source files) from the original repository that are required
for the production of these artifacts as they are part of the package
(provided that the original sources are also packaged into the wheel).

Using registered .scss with other Calmjs Node.js/JavaScript toolchains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While the registry system is designed to be as extensible and reuseable
as much as possible, those specific underlying tools may expect a
different complete module name as they may require specific loader
string prepended to the stylesheet.  This topic will require more
exploration for better overall integration, despite the building blocks
to acheive this is available in the base/generic form.


Troubleshooting
---------------

UserWarning: Unknown distribution option:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During setup and installation using the development method, if this
warning message is shown, please ensure the egg metadata is correctly
generated by running ``python setup.py egg_info`` in the source
directory, as the package |calmjs| was not available when the setup
script was initially executed.

CalmjsSassyRuntimeError: missing required package 'libsass'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please install the |libsass-python| package; this can be achieved by
running:

.. code:: sh

    $ pip install libsass

CalmjsSassyRuntimeError: failed to compile with libsass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This can be caused by syntax errors within the styling rules, which
should be reported as part of the output.  Generation using the built-in
``calmjs scss`` runtime may return more detailed debugging information
using the relevant flags as documented by the ``--help`` flag.

Internal Error: Data context created with empty source string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While using the libsass interfacing runtime or toolchain (e.g. the
default ``calmjs scss`` runtime), if the provided package does not
include (export) a ``.scss`` file for the specified entry point name
(the default is ``index``, and so the package must export a
``index.scss`` file at the location registered in the ``calmjs.scss``
registry), nothing will be imported thus the source string will be
empty, resulting in ``libsass`` aborting the execution.


Contribute
----------

.. _issue tracker:

- Issue Tracker: https://github.com/calmjs/calmjs.sassy/issues
- Source Code: https://github.com/calmjs/calmjs.sassy


Legal
-----

The |calmjs.sassy| package is part of the calmjs project.

The calmjs project is copyright (c) 2016 Auckland Bioengineering
Institute, University of Auckland.  |calmjs.sassy| is licensed under
the terms of the GPLv2 or later.
