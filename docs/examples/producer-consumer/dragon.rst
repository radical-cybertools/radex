Dragon Examples
===============

- A producer/consumer exchange using the Dragon DDict backend.
- Scalar and tensor writes in producer and reads in consumer.
- A Python driver that provisions a DDict and launches both binaries.

Key Files
---------

- driver.py: creates and serializes DDict, then launches producer and consumer.
- producer.cpp: writes scalar and tensor values.
- consumer.cpp: reads values back and prints data plus dimensions.

Run
---

.. code-block:: bash

   python driver.py

Notes
-----

- The driver passes a serialized DDict descriptor via SERIALIZED_DDICT.
