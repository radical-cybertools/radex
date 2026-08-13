import filecmp


def test_run_example(example, tmp_path):
    returncode, out, err = example.run(where=tmp_path)
    assert returncode == 0
    assert filecmp.cmp(out, example.expected_stdout)
