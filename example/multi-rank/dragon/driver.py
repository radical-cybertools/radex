import os
import pathlib

import dragon
from dragon.data.ddict import DDict
from dragon.native.process import ProcessTemplate
from dragon.native.process_group import ProcessGroup

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
EXAMPLES_BIN_DIR = ROOT / "install" / "bin" / "examples"


def main() -> int:
    NUM_PRODUCER_RANKS = 4

    pg = ProcessGroup(restart=False, ignore_error_on_exit=True)
    dd = DDict(managers_per_node=1, n_nodes=1, wait_for_keys=True, working_set_size=2)
    serial_dd = dd.serialize()

    templates = [
        *(
            ProcessTemplate(
                target=os.fspath(EXAMPLES_BIN_DIR / "dragon-multi-rank-producer"),
                args=(serial_dd, str(i), str(NUM_PRODUCER_RANKS)),
            )
            for i in range(NUM_PRODUCER_RANKS)
        ),
        ProcessTemplate(
            target=os.fspath(EXAMPLES_BIN_DIR / "dragon-multi-rank-consumer"),
            args=(serial_dd, str(NUM_PRODUCER_RANKS)),
        ),
    ]

    for template in templates:
        pg.add_process(nproc=1, template=template)

    pg.init()
    try:
        pg.start()
        pg.join()
    finally:
        pg.close()
    dd.destroy()


if __name__ == "__main__":
    raise SystemExit(main())
