from smartsim import Experiment
import os
import pathlib
import time

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent.parent
BUILD = ROOT / "build"


def main() -> int:
    exp = Experiment("cpp-sr-client-exchange")

    db = exp.create_database(db_nodes=1, interface="hsn0")

    producer_settings = exp.create_run_settings(os.fspath(BUILD / "redis-cpp-producer"))
    producer = exp.create_model("producer", producer_settings)

    consumer_settings = exp.create_run_settings(os.fspath(BUILD / "redis-cpp-consumer"))
    consumer = exp.create_model("consumer", consumer_settings)

    exp.generate(db, producer, consumer)
    exp.start(db, block=False)
    time.sleep(3)

    try:
        exp.start(producer, block=True)
        exp.start(consumer, block=True)
    finally:
        exp.stop(db)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
