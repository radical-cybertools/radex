SmartRedis Examples
===================

- A producer/consumer exchange using the SmartRedis backend.
- Scalar and tensor writes in producer and reads in consumer.
- A Python SmartSim driver that launches a database and then both binaries.

Key Files
---------

- driver.py: starts a SmartSim database and launches producer and consumer models.
- producer.cpp: writes scalar and tensor values.
- consumer.cpp: reads values back and prints data plus dimensions.

Run
---

.. code-block:: bash

   python driver.py

Notes
-----

- The example requires SmartSim and SmartRedis runtime dependencies.
