import pathlib
import os
import dragon
from dragon.data.ddict import DDict
from dragon.native.process import ProcessTemplate, Process

HERE = pathlib.Path(__file__).parent

def main() -> int:
    dd = DDict(managers_per_node=1, n_nodes=1, trace=False)
    serial_dd = dd.serialize()
    producer_tmpl = ProcessTemplate(
            target=os.fspath(HERE / "producer"),
            env={"SERIALIZED_DDICT": serial_dd}
            )
    consumer_tmpl = ProcessTemplate(
            target=os.fspath(HERE / "consumer"),
            env={"SERIALIZED_DDICT": serial_dd}
            )

    print("==> Running Producer...", flush=True)
    producer = Process.from_template(producer_tmpl)
    producer.start()
    producer.join()
    print("==> Producer Joined", flush=True)

    print("==> Running Consumer...", flush=True)
    consumer = Process.from_template(consumer_tmpl)
    consumer.start()
    consumer.join()
    print("==> Consumer Joined", flush=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
