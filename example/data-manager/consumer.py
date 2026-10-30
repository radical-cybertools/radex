from __future__ import annotations

import pprint
import time
import os
import numpy as np
import textwrap

from radex.clients.core import DragonClient as Client
from radex.data.manager import Locator, ManagedApplication


def main() -> int:
    my_app = ManagedApplication(
        application="consumer", manager=Locator.from_environment()
    )
    my_app.manager.await_api(timeout=60)

    # TODO: Move this onto manager attr itself??
    while not my_app.manager.is_initialized():
        time.sleep(1)

    serial_dd = os.environ.get("SERIALIZED_DDICT", None)
    if serial_dd is None:
        raise ValueError("Failed to get serialized ddict")
    client = Client(serial_dd, 5)

    # TODO: make this one handle per request, have this take in a full set of metadata
    handle_0 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "0"}})
    handle_1 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "1"}})
    handle_2 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "2"}})
    handle_3 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "3"}})

    tensor_0 = client.wait_for_tensor(handle_0, 15)
    tensor_1 = client.wait_for_tensor(handle_1, 15)
    tensor_2 = client.wait_for_tensor(handle_2, 15)
    tensor_3 = client.wait_for_tensor(handle_3, 15)

    final_tensor = np.stack([tensor_0, tensor_1, tensor_2, tensor_3])

    print(
        textwrap.dedent(f"""\
        -------------------------------
        | Client Created Final Tensor |
        -------------------------------
          \\- Data: {final_tensor.ravel()}
          \\- Dims: {final_tensor.shape}
          \\- Type: {final_tensor.dtype}
        """),
        flush=True,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
