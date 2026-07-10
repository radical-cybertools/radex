Installation
============

Prerequisites
-------------

- CMake 3.13 or newer
- A C++17-compatible compiler
- Backend dependencies for at least one transport:
  - SmartRedis development package, and/or
  - Dragon development headers and library

Build From Source
-----------------

.. code-block:: bash

   cmake -S . -B build -DCMAKE_INSTALL_PREFIX=/path/to/install/locaiton
   cmake --build build
   cmake --install build

Backend Selection
-----------------

RaDex can be configured to compile with one or both backends:

.. code-block:: bash

   cmake -S . -B build -DBUILD_SMARTREDIS=ON -DBUILD_DRAGON=ON

Disable a backend explicitly when dependencies are unavailable:

.. code-block:: bash

   cmake -S . -B build -DBUILD_SMARTREDIS=OFF -DBUILD_DRAGON=ON

