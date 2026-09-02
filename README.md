# The Radical Data Exchanger (radex)

[![Documentation](https://img.shields.io/badge/docs-available-blue.svg)](https://radical-cybertools.github.io/radex/)

**radex** is a lightweight, high-performance data exchange layer for moving scalars and tensors between the heterogeneous components of an HPC-AI workflow — MPI simulations and Python functions without going through a filesystem.

It is co-developed by [HPE](https://hpe.com) and the [RADICAL Cybertools](https://radical-cybertools.github.io) team and used by other RCT projects (such as [RHAPSODY](https://radical-cybertools.github.io/rhapsody)) to move data in-memory over interconnects.

The library is built around a C++ core (with a Cython-based Python client) for putting and getting named values into shared backends such as Dragon's Distributed Dictionary (DDict) or Redis, so producers and consumers written in different languages can exchange data directly.

## Key Features

- **Typed put/get API** — Exchange scalars (`int32`, `int64`, `float`, `double`) and n-dimensional tensors by name (`OutgoingHandle` / `IncomingHandle`).
- **Multiple backends** — Use the same API with different clients to interact with [Dragon](https://dragonhpc.github.io/dragon/doc/_build/html/index.html) DDict or [SmartRedis](https://github.com/CrayLabs/SmartRedis).
- **C++ and Python clients** — A C++ core and a Cython-based Python client (`radex`) built against the same compiled core, so both languages can read/write the same keys.

## Installation

radex is currently distributed as source only: a C++ core library and an optional Cython-based Python client that binds to it. Installation means building from source.

**Prerequisites**

- **CMake** >= 3.13
- **C++17** compiler
- A backend library, matching what you enable at configure time:
  - [Dragon](https://dragonhpc.github.io/dragon/doc/_build/html/index.html) (`BUILD_DRAGON`, on by default)
  - [SmartRedis](https://github.com/CrayLabs/SmartRedis) (`BUILD_SMARTREDIS`, on by default)
- **Python** 3.12, `Cython`, and `numpy` if building the Python client (`ENABLE_PYTHON`, on by default)

**Quick build**

```bash
git clone https://github.com/radical-cybertools/radex.git
cd radex
cmake -S . -B build -DCMAKE_INSTALL_PREFIX=install
cmake --build build --target install
```

**Verify**

```bash
ls install/lib
# and, if you built the Python client:
python3 -c "import radex; from radex.clients.core import DragonClient"
```

See [Building From Source](docs/getting-started/building-from-source.md) for backend-specific configuration (CMake options, environment variables, `dragon-config`, disabling backends) and [Fetching Backends](docs/getting-started/fetching-backends.md) for installing the Dragon and SmartRedis libraries.

## Quick Start

A minimal example exchanging a value between Python and C++ using the Dragon DDict backend.

Start a DDict and a Python client:

```python
from dragon.data.ddict import DDict
from radex.clients.core import DragonClient as Client
from radex.handles.handles import IncomingHandle, OutgoingHandle

dd = DDict(managers_per_node=1, n_nodes=1)
serialized_dd = dd.serialize()

client = Client(serialized_dd, 5)  # 5 second timeout
client.put_scalar(OutgoingHandle("greeting-count"), 1)
```

Pass the serialized descriptor to a separate process (for example, via an environment variable) and attach a C++ client to the same DDict:

```cpp
#include "radex/dragon.hpp"
#include "radex/handles.hpp"

char *serialized_dd = getenv("SERIALIZED_DDICT");
timespec timeout{5, 0};
radex::drg::ddict::Client client{serialized_dd, &timeout};

int32_t value = client.get_scalar<int32_t>(
    radex::data::IncomingHandle{"greeting-count"});
```

Both clients also support n-dimensional tensors:

```python
import numpy as np
client.put_tensor(OutgoingHandle("weights"), np.zeros((4, 4), dtype=np.float64))
```

```cpp
client.put_tensor<double>(radex::data::OutgoingHandle{"weights"},
                          {4, 4}, std::vector<double>(16, 0.0));
```

See the [Quick Start](docs/getting-started/quick-start.md) and [Examples](docs/examples/index.md) for realistic driver/worker setups (MPI + Dragon DDict, C++-to-C++, and Python-to-C++ exchange).

## Documentation

- [Getting Started](docs/getting-started/index.md) — install, build, and run your first data exchange.
- [Examples](docs/examples/index.md) — complete, real-world usage patterns.
- [API Reference](docs/api/index.md) — the full set of client methods and handle types.
- [About](docs/about.md) — background, contributors, and links.

## Primary Developers

| Name | Affiliation |
| --- | --- |
| Matt Drozt | HPE |
| Andrew Shao | HPE |
| Aymen Alsaadi | Rutgers University |
| Kent Lee | HPE |
| Yian Chen | HPE |

## License

radex is distributed under the license in [LICENSE](https://github.com/radical-cybertools/RaDex/blob/main/LICENSE).

## Links

- [Source code](https://github.com/radical-cybertools/radex)
- [Issue tracker](https://github.com/radical-cybertools/radex/issues)