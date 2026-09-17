import subprocess

import pytest

CPP_TEST_BINARIES = [
    "test-local-client",
]

C_TEST_BINARIES = [
    "test-c-interface",
]


@pytest.mark.parametrize("binary_name", CPP_TEST_BINARIES)
def test_cpp(binary_name, resolve_bin_path):
    exe_path = resolve_bin_path(binary_name)
    result = subprocess.run([str(exe_path)], capture_output=True, text=True)

    assert result.returncode == 0, (
        f"C++ binary failed: {exe_path}\n"
        f"exit code: {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.parametrize("binary_name", C_TEST_BINARIES)
def test_c_interface(binary_name, resolve_bin_path):
    """Test C interface using in-memory backend.

    The C test uses the in-memory (unordered map) backend and doesn't require
    external services like Redis or Dragon.
    """
    exe_path = resolve_bin_path(binary_name)
    result = subprocess.run([str(exe_path)], capture_output=True, text=True)

    assert result.returncode == 0, (
        f"C interface test failed: {exe_path}\n"
        f"exit code: {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
