calmjs.sassy
============

Package for extending the `Calmjs framework`_ to support the usage of
|sass|_ in a manner that crosses Python package boundaries by exposing
an  ``import`` system that mimics the package namespaces available
within the current Python environment, such that styling rules can be
more easily propagated to their dependants.  This facilitates the reuse
of styling rules declared by Python packages' dependencies in a manner
more familiar to users of the given Python environments by reusing the
same names as the namespaces they may be using.

.. image:: https://travis-ci.org/calmjs/calmjs.sassy.svg?branch=master
    :target: https://travis-ci.org/calmjs/calmjs.sassy
.. image:: https://ci.appveyor.com/api/projects/status/1gei512socwe8nho/branch/master?svg=true
    :target: https://ci.appveyor.com/project/metatoaster/calmjs-sassy/branch/master
.. image:: https://coveralls.io/repos/github/calmjs/calmjs.sassy/badge.svg?branch=master
    :target: https://coveralls.io/github/calmjs/calmjs.sassy?branch=master

.. |calmjs| replace:: ``calmjs``
.. |calmjs.sassy| replace:: ``calmjs.sassy``
.. |sass| replace:: ``sass``
.. _Calmjs framework: https://pypi.python.org/pypi/calmjs
.. _calmjs: https://pypi.python.org/pypi/calmjs
.. _sass: https://sass-lang.com/

Introduction
------------

TODO to be written

Features
--------

How |calmjs.sassy| works
~~~~~~~~~~~~~~~~~~~~~~~~

TODO to be written


Installation
------------

When this package is officially released, the following may be done; for
now please continue onto the alternative installation method.

.. code:: sh

    $ pip install calmjs.sassy

Alternative installation methods (advanced users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Development is still ongoing with |calmjs.sassy|; the development
version may be installed through git like so:

.. code:: sh

    $ pip install calmjs
    $ pip install git+https://github.com/calmjs/calmjs.sassy.git#egg=calmjs.sassy

Alternatively, the git repository can be cloned directly and execute
``python setup.py develop`` while inside the root of the source
directory.

Keep in mind that |calmjs| MUST be available before the ``setup.py``
within the |calmjs.sassy| source tree is executed, for it needs the
``package_json`` writing capabilities in |calmjs|.  Alternatively,
please execute ``python setup.py egg_info`` if any message about
``Unknown distribution option:`` is noted during the invocation of
``setup.py``.

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

TODO build this feature


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
``*.scss`` files within those directories.  Finally, as a consequence of
how the imports are done, it is recommended that no relative imports are
to be used.

Putting this together, the ``setup.py`` file should contain the
following:

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

Declaring prebuilt, standard CSS bundle for the Python package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, to complete the Python package deployment story, the process
should include the automatic generation and inclusion of the stylesheet
artifacts in the resulting Python wheel.  This can be achieved by
specifying an entry in the ``calmjs.artifacts`` registry, with the key
being the filename of the artifact and the value being the import
location to a builder.  A default builder function provided at
``calmjs.sassy.artifact:complete_css`` will enable the generation
of a complete stylesheet:

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
process.  Consider this ``setup.py``:

.. code:: Python

    setup(
        name='example.package',
        # ... other required fields truncated
        build_calmjs_artifacts=True,
        entry_points="""
        # ... other entry points truncated
        [calmjs.module]
        example.package = example.package

        [calmjs.artifacts]
        example.bundle.css = calmjs.sassy.artifact:complete_css
        """,
    )

Building the wheel using ``setup.py`` may result in something like this.

.. code::

    $ python setup.py bdist_wheel
    ...


Troubleshooting
---------------

UserWarning: Unknown distribution option:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During setup and installation using the development method, if this
warning message is shown, please ensure the egg metadata is correctly
generated by running ``python setup.py egg_info`` in the source
directory, as the package |calmjs| was not available when the setup
script was initially executed.


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
