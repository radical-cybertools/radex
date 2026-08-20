import os
import pathlib
import shutil
import textwrap
import time

from smartsim import Experiment

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
EXAMPLES_BIN_DIR = ROOT / "install" / "bin" / "examples"


def main() -> int:
    NUM_PRODUCER_RANKS = 4

    exp_name = "sr-multi-rank-client-exchange"
    producer_name = "producer-{}"
    consumer_name = "consumer"

    os.environ["SR_LOG_LEVEL"] = "QUIET"
    if (HERE / exp_name).exists():
        shutil.rmtree(HERE / exp_name)

    exp = Experiment(exp_name, launcher="local")

    db = exp.create_database(db_nodes=1, interface="lo")

    producer_settings = [
        exp.create_run_settings(
            os.fspath(EXAMPLES_BIN_DIR / "redis-multi-rank-producer"),
            exe_args=[str(i), str(NUM_PRODUCER_RANKS)],
        )
        for i in range(NUM_PRODUCER_RANKS)
    ]
    producers = [
        exp.create_model(producer_name.format(i), rs)
        for i, rs in enumerate(producer_settings)
    ]
    consumer_settings = exp.create_run_settings(
        os.fspath(EXAMPLES_BIN_DIR / "redis-multi-rank-consumer"),
        exe_args=[str(NUM_PRODUCER_RANKS)],
    )
    consumer = exp.create_model("consumer", consumer_settings)

    exp.generate(db, *producers, consumer)
    exp.start(db, block=False)
    time.sleep(3)

    try:
        exp.start(*producers, consumer, block=True, monitor=False)
    finally:
        exp.stop(db)

    for i in range(NUM_PRODUCER_RANKS):
        print("PRODUCER OUTPUT:")
        with open(
            HERE
            / exp_name
            / producer_name.format(i)
            / f"{producer_name.format(i)}.out",
            "r",
            encoding="utf-8",
        ) as f:
            print(textwrap.indent(f.read(), "    "))

    print("CONSUMER OUTOUT:")
    with open(
        HERE / exp_name / consumer_name / f"{consumer_name}.out", "r", encoding="utf-8"
    ) as f:
        print(textwrap.indent(f.read(), "    "))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
