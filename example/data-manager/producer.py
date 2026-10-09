from __future__ import annotations

from mpi4py import MPI
from radex.data.manager import DataManager


def main() -> int:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    this_proc = DataManager.register_process(application="consumer")

    # on the producer side
    out_handle = this_proc.get_outgoing_handle(metadata={...})
    # ^^^ this handle will rich, do not need to check that it is actually used
    # to set tensor v scalar, correct dtpye, etc.

    # TODO: these are notes for a consumer api
    # have this take in a full set of metadata
    handle = this_proc.get_incoming_handle(
        descrition={"short-name": "some-data-1", "dtype": "float32", "metadata": {}}
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
