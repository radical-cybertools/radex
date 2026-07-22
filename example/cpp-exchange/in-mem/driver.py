import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent.absolute()
ROOT = HERE.parent.parent.parent
BUILD = ROOT / "build"


def main() -> int:
    subprocess.run((BUILD / "in-mem-poc",), check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
