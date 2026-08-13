import os

import pytest
from dragon.data.ddict import DDict

import radex


def test_init_raises_if_wait_for_keys_is_disabled(_requires_dragon_runtime):
    ddict = DDict(managers_per_node=1, n_nodes=1, wait_for_keys=False)
    with pytest.raises(RuntimeError, match=r"wait_for_keys"):
        radex.DragonClient(descriptor=ddict.serialize(), timeout=1)


def test_init_from_env(_persistent_ddict_client):
    os.environ["RADEX_STORE"] = _persistent_ddict_client.serialize()
    client = radex.DragonClient()
    key = "some-value"
    some_value = 0.1
    client.put_scalar(key, some_value)
    ret_val = client.get_scalar(key)
    assert some_value == ret_val
