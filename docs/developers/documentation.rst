Documentation
=============

Prerequisites
-------------
- Doxygen
- Sphinx and extensions (see below)

To install sphinx dependencies:

.. code-block:: bash

   python -m pip install -r docs/requirements.txt

Building
--------

.. code-block:: bash

   cmake -S docs -B docs/build
   cmake --build docs/build

The rendered documents will be found in `docs/build/sphinx`