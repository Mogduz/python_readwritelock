# python_readwritelock

A simple Reader-Writer lock for Python threads.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Context Managers](#context-managers)
- [API](#api)
- [Thread Safety Details](#thread-safety-details)
- [Project Structure](#project-structure)
- [Tests](#tests)
- [Development & Contribution](#development--contribution)
- [License](#license)
- [Authors](#authors)

## Overview

This repository provides the `ReadWriteLock` class, which allows multiple concurrent read accesses or a single exclusive write access in Python threads. Internally, it uses a `threading.Condition` to synchronize readers and writers without starvation.

## Features

- Multiple concurrent readers
- Single exclusive writer
- Convenient context manager support
- Fairness: writers wait until all readers have finished
- Compatible with Python ≥ 3.7

## Installation

```bash
git clone https://github.com/Mogduz/python_readwritelock.git
cd python_readwritelock
pip install .
# Or directly:
pip install git+https://github.com/Mogduz/python_readwritelock.git
```

## Usage

### Basic Usage

```python
from readwritelock import ReadWriteLock

lock = ReadWriteLock()

# Reader access
with lock.read_lock():
    # critical read section
    pass

# Writer access
with lock.write_lock():
    # critical write section
    pass
```

### Context Managers

Alternatively, use the methods directly:

```python
lock.acquire_read()
try:
    # read section
    pass
finally:
    lock.release_read()
```

```python
lock.acquire_write()
try:
    # write section
    pass
finally:
    lock.release_write()
```

## API

### Class `ReadWriteLock`

#### Constructor

- `__init__()`: Initializes the internal `Condition` and reader counter.

#### Methods

- `acquire_read()`: Acquires a shared read lock (increments counter).
- `release_read()`: Releases the shared read lock (decrements counter and notifies writers).
- `acquire_write()`: Acquires an exclusive write lock (blocks until no readers are active).
- `release_write()`: Releases the write lock.

#### Context Managers

- `read_lock()`: Context manager for read access.
- `write_lock()`: Context manager for write access.

## Thread Safety Details

- Uses `threading.Condition` with an internal `Lock`.
- Readers increment/decrement a counter; writers block while the counter > 0.
- `notify_all()` signals waiting writers after the last reader releases.

## Project Structure

```
python_readwritelock/
├── readwritelock/
│   ├── __init__.py
│   └── readwritelock.py
├── tests/
│   └── test_readwritelock.py
├── conftest.py
├── pyproject.toml
├── requirements.txt
└── LICENSE
```

## Tests

The test suite is based on `pytest` with the following plugins:

- `pytest-cov` (coverage measurement)
- `pytest-mock` (mocking/patching)
- `pytest-xdist` (parallel testing)
- `pytest-asyncio` (async tests)
- `pytest-benchmark` (performance benchmarks)
- `pytest-html` (HTML report)

Run tests with:

```bash
pytest
```

Reports are generated in the `reports/` directory by default.

## Development & Contribution

Contributions are welcome! Please open an issue for bug reports or feature requests and submit pull requests. Make sure all tests pass.

## License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.

## Authors

- Mogduz  
- Initial release: April 18, 2025
