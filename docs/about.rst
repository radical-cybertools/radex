About
=====

RaDex provides a C++ data exchange abstraction with multiple backend
implementations.

Current backends include:
- DDict from DragonHPC using the Serializable features
- Redis Database using the SmartRedis client

The DragonHPC DDict should be considered as the first-choice as its RDMA communication
layer and (optional) integration with libfabric makes it the lower-latency,
high-bandwidth, scaleable backend. The Redis-backend is primarily for backwards
compatibility with SmartSim/SmartRedis applications and to validate the backend-agnostic
approach for RadEx.
