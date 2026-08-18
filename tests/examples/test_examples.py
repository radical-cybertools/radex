def test_run_example(example, tmp_path):
    returncode, out, err = example.run(where=tmp_path)
    assert returncode == 0

    print("Expected:")
    print("---------")
    with open(example.expected_stdout, "r", encoding="utf-8") as f:
        print(f.read())

    print("\nGot:")
    print("----")
    with open(out, "r", encoding="utf-8") as f:
        print(f.read())

    with (
        open(out, "r", encoding="utf-8") as fh,
        open(example.expected_stdout, "r", encoding="utf-8") as xfh,
    ):
        for line, xline in zip(fh, xfh):
            assert line.strip() == xline.strip()
