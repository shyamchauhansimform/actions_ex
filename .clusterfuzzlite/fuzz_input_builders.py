"""
ClusterFuzzLite/OSS-Fuzz harness for the unsanitised input-builder functions
extracted from vuln_app.py (build_user_query, build_ping_command).

These builders are the injection sinks behind the /user (SQLi) and /ping
(command injection) demo routes. They are fuzzed directly, as pure
functions, so the fuzzer can explore malformed/adversarial input without
ever touching sqlite3 or a real shell.
"""
import atheris
import sys

with atheris.instrument_imports():
    import vuln_app


def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    text = fdp.ConsumeUnicodeNoSurrogates(fdp.remaining_bytes())

    query = vuln_app.build_user_query(text)
    assert isinstance(query, str)
    assert text in query
    assert query.startswith("SELECT * FROM users WHERE id = ")

    command = vuln_app.build_ping_command(text)
    assert isinstance(command, str)
    assert text in command
    assert command.startswith("echo Pinging ")


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
