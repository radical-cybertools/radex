from __future__ import annotations

from mpi4py import MPI
from radex.data.manager import DataManager


def main() -> int:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    dm_client = DataManagerClient(hostname=os.enviorn[...], port=os.enviorn[...])

    # on the producer side
    # TODO: make this one handle per req
    # TODO: need to allow this to filter based on metadata and error if not
    #       unique or none
    # TODO: start with this and profile, see how many keys can be fetched
    #       before one minute, then optimize
    out_handle: OutgoingHandle = this_proc.get_outgoing_handles()

    # TODO: work toward this??
    # out_handle: list[OutgoingHandle] = (
    #     this_proc
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .get_outgoing(...)
    #     .collect()
    # )

    # ^^^ this handle will rich, do not need to check that it is actually used
    # to set tensor v scalar, correct dtpye, etc.

    # TODO: these are notes for a consumer api
    # TODO: make this one handle per request
    # have this take in a full set of metadata
    handle: IncomingHandle = this_proc.get_incoming_handle(
        descrition={"dtype": "float32", "metadata": {"what-is": "temperateue"}}
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
