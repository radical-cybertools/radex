from __future__ import annotations

import pprint
import time

from radex.data.manager import Locator, ManagedApplication

# from mpi4py import MPI


def main() -> int:
    # comm = MPI.COMM_WORLD
    # rank = comm.Get_rank()

    my_app = ManagedApplication(
        application="producer", manager=Locator.from_environment()
    )
    my_app.manager.await_api(timeout=60)

    # TODO: Move this onto manager attr itself??
    while not my_app.manager.is_initialized():
        time.sleep(1)

    # on the producer side
    # TODO: start with this and profile, see how many keys can be fetched
    #       before one minute, then optimize
    handle_0 = my_app.get_outgoing_handle({"metadata": {"which-rank": "0"}})
    handle_1 = my_app.get_outgoing_handle({"metadata": {"which-rank": "1"}})
    handle_2 = my_app.get_outgoing_handle({"metadata": {"which-rank": "2"}})
    handle_3 = my_app.get_outgoing_handle({"metadata": {"which-rank": "3"}})

    # TODO: Work toward this?? Might be impossible to type in C++
    # out_handle: list[OutgoingHandle] = (
    #     this_proc
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .collect()
    # )

    # TODO: We want these handles to be rich. We should not need to check that
    #       it is actually used to set tensor v scalar, correct dtpye, etc.
    #       That we will make the responsibility of the client

    print("Producer is writing:")
    print("--------------------")
    pprint.pprint([handle_0, handle_1, handle_2, handle_3])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
