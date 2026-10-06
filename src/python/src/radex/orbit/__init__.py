"""radex data exchange over RADICAL ORBIT.

- `radex.orbit.client.OrbitClient`: radex put/get API over ORBIT (pure Python).
- `radex.orbit.plugin.PluginRadex`: the ORBIT plugin serving those calls next
  to a store; registered via the ``radical.orbit.plugins`` entry point.

Install with the ``orbit`` extra: ``pip install radex[orbit]``.  Importing
this package registers the plugin class, which a consumer needs for
``runtime.get_plugin(endpoint, 'radex')`` to return an `OrbitClient`.
"""

from radex.orbit.client import OrbitClient
from radex.orbit.plugin import PluginRadex

__all__ = ["OrbitClient", "PluginRadex"]
