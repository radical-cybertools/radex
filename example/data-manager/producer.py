from __future__ import annotations

from radex.data.manager import DataManager
from mpi4py import MPI


def main() -> int:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    this_proc = DataManager.register_process(application="producer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
