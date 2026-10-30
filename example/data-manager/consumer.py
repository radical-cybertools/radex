from __future__ import annotations

import pprint
import time

from radex.data.manager import Locator, ManagedApplication


def main() -> int:
    my_app = ManagedApplication(
        application="consumer", manager=Locator.from_environment()
    )
    my_app.manager.await_api(timeout=60)

    # TODO: Move this onto manager attr itself??
    while not my_app.manager.is_initialized():
        time.sleep(1)

    # TODO: make this one handle per request, have this take in a full set of metadata
    handle_0 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "0"}})
    handle_1 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "1"}})
    handle_2 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "2"}})
    handle_3 = my_app.get_incoming_handle(description={"metadata": {"which-rank": "3"}})

    print("Consumer is reading:")
    print("--------------------")
    pprint.pprint([handle_0, handle_1, handle_2, handle_3])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
