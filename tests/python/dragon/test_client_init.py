import pytest
from dragon.data.ddict import DDict

import radex


def test_init_raises_if_wait_for_keys_is_disabled(_requires_dragon_runtime):
    ddict = DDict(managers_per_node=1, n_nodes=1, wait_for_keys=False)
    with pytest.raises(RuntimeError, match=r"wait_for_keys"):
        radex.DragonClient(descriptor=ddict.serialize(), timeout=1)
