In-Memory Interface Example
===========================

- A proof-of-concept backend implementing the RaDex IClient interface with an
  in-process unordered_map.
- The same scalar and tensor helper APIs without an external transport backend.

Key Files
---------

- proof_of_concept_iface.cpp: defines an in-memory IClient implementation and
  demonstrates scalar/tensor put/get operations.

Run
---

.. code-block:: bash

   ./proof

Notes
-----

- This example is self-contained and does not require Dragon or SmartRedis.
- It is useful for understanding the typed helper layer on top of put_bytes/get_bytes.
