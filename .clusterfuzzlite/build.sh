#!/bin/bash -eu

cp "$SRC/actions_ex/.clusterfuzzlite/fuzz_input_builders.py" "$SRC/"
compile_python_fuzzer fuzz_input_builders.py
