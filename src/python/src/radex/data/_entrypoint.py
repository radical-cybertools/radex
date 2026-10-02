import subprocess
import sys


def main() -> int:
    proc = subprocess.run(
        (
            sys.executable,
            "-m",
            "flask",
            "--app",
            "radex.data._application:app",
            "run",
            "--host",
            "127.0.0.1",
            "--port",
            "13254",
        ),
        capture_output=False,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
