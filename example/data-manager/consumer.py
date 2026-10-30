def main() -> int:
    # TODO: these are notes for a consumer api
    # TODO: make this one handle per request
    # have this take in a full set of metadata
    handle = this_proc.get_incoming_handle(
        descrition={"dtype": "float32", "metadata": {"what-is": "temperateue"}}
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
