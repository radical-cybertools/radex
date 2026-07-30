import dataclasses
import os
import pathlib
import textwrap
import time

import dragon
import numpy as np
from dragon.data.ddict import DDict
from dragon.native.process import Process, ProcessTemplate

from radex import DragonClient as Client

HERE = pathlib.Path(__file__).parent.absolute()
ROOT = HERE.parent.parent.parent
EXAMPLES_BIN_DIR = ROOT / "install" / "bin" / "examples"


def main() -> int:
    dd = DDict(managers_per_node=1, n_nodes=1, trace=False)
    serial_dd = dd.serialize()
    app_tmpl = ProcessTemplate(
        target=os.fspath(EXAMPLES_BIN_DIR / "dragon-cpp-with-py"),
        env={"SERIALIZED_DDICT": serial_dd},
    )
    app = Process.from_template(app_tmpl)

    print(f"Driver: Making client")
    client = Client(serial_dd, 5)

    print(f"Driver: Starting app")
    app.start()
    try:
        time.sleep(3)
        print("Driver: Setting Int")
        client.put_scalar("py-int", 123)

        time.sleep(3)
        print("Driver: Setting Double")
        client.put_scalar("py-double", 9.87)

        time.sleep(3)
        print("Driver: Setting Numpy Int")
        client.put_scalar("py-np-float", np.float32(45.6))

        time.sleep(3)
        print("Driver: Setting Int Tensor")
        client.put_tensor("py-int-tensor", np.arange(4, dtype=np.int32))

        time.sleep(3)
        print("Driver: Setting Float Tensor")
        client.put_tensor(
            "py-float-tensor", np.arange(12, dtype=np.float64).reshape((6, 2))
        )

        print(f"Driver: Looking for keys")
        print_scalar(client, "cpp-double")
        print_scalar(client, "cpp-int")
        print_tensor(client, "cpp-double-tensor")
        print_tensor(client, "cpp-long-tensor")

        print("Driver: Setting a py object")
        py_obj_key = "my-py-obj"
        obj = C("spam-and-eggs")
        client.put_picklable(py_obj_key, obj)
        print("Driver: Getting a py object")
        recv = client.get_picklable(py_obj_key)
        print(f"Driver: Got object `{recv}`")
    finally:
        app.join()

    return 0


def poll_for_key(client, key, max_attempts=10):
    while not client.contains(key):
        print(f"Driver: Waiting for key `{key}`")
        if max_attempts == 0:
            raise RuntimeError(f"Too many attempts polling for `{key}`")
        max_attempts -= 1
        time.sleep(1)


def print_scalar(client, key):
    print(f"Driver: Waiting for scalar key `{key}`")
    scalar = client.wait_for_scalar(key, 10)
    print(textwrap.dedent(f"""\
        Driver: Got scalar:
                |- Type: {scalar.dtype}
                \\- Value: {scalar}
        """))


def print_tensor(client, key):
    print(f"Driver: Waiting for tensor key `{key}`")
    tensor = client.wait_for_tensor(key, 10)
    print(textwrap.dedent(f"""\
        Driver: Got tensor:
                |- Type: {tensor.dtype}
                |- Dims: {tensor.shape}
                \\- Data: {tensor.ravel()}
        """))


@dataclasses.dataclass(frozen=True)
class C:
    msg: str


if __name__ == "__main__":
    raise SystemExit(main())
