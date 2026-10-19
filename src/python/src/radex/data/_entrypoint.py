import argparse
import subprocess
import sys

from radex.data._utils import consts


def main() -> int:
    args = _parse_args()
    proc = subprocess.run(
        (
            sys.executable,
            "-m",
            "flask",
            "--app",
            consts.MNGR_APPLICATION,
            "run",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ),
        capture_output=False,
    )
    return proc.returncode


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--port", type=int, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
