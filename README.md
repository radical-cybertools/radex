# RaDex
Data Exchange Layer for RCT

## Documentation

This repository now includes a rudimentary documentation pipeline based on:

- Doxygen for C++ API extraction
- Sphinx for HTML site generation
- Breathe to import Doxygen XML into Sphinx

### Build Docs

1. Install Python dependencies:

	pip install -r docs/requirements.txt

2. Configure CMake with documentation enabled:

	cmake -S . -B build -DBUILD_DOCS=ON

3. Build docs:

	cmake --build build --target docs

Generated HTML will be available under `build/docs/sphinx`.
