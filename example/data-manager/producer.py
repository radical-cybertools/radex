from __future__ import annotations

from mpi4py import MPI
from radex.data.manager import DataManager


def main() -> int:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    this_proc = DataManager.register_process(application="producer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
