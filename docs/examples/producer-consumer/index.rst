Producer/Consumer Examples
==========================

A simple producer/consumer example type where data is passed using different
backend transports and interface implementations.

Available backends
------------------

- :doc:`dragon`: Producer/consumer exchange via Dragon DDict.
- :doc:`redis`: Producer/consumer exchange via SmartRedis.
- :doc:`in-mem`: In-process transport-free variant based on `IClient`.

.. toctree::
   :maxdepth: 1
   :hidden:

   dragon
   redis
   in-mem
