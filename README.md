# ReadWriteLock

A simple **Reader-Writer Lock** implementation for Python threads, enabling multiple concurrent readers or a single exclusive writer.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Direct Methods](#direct-methods)
- [API Reference](#api-reference)
- [Thread Safety Details](#thread-safety-details)
- [Performance](#performance)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)
- [Authors](#authors)

## Overview
The `ReadWriteLock` class provides a synchronization primitive that allows:
- **Multiple concurrent readers**: Threads can acquire the lock for reading simultaneously.
- **Single exclusive writer**: Only one writer can hold the lock at a time, and no readers can hold it during writing.

This pattern helps optimize performance in scenarios with frequent read operations and infrequent writes.

## Features
- Multiple simultaneous readers
- Single exclusive writer
- Context manager support (`with` statement)
- Fairness: writers wait until all active readers release the lock
- Compatible with Python ≥ 3.7

## Installation
Clone the repository and install via pip:

```bash
git clone https://github.com/Mogduz/python_readwritelock.git
cd python_readwritelock
pip install .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/Mogduz/python_readwritelock.git
```

Alternatively, if published on PyPI:

```bash
pip install readwritelock
```

## Usage

### Basic Usage
```python
from readwritelock import ReadWriteLock

lock = ReadWriteLock()

# Shared read
with lock.read_lock():
    # perform thread-safe read operations
    data = shared_resource.read()

# Exclusive write
with lock.write_lock():
    # perform thread-safe write operations
    shared_resource.update(new_value)
```

### Direct Methods
```python
lock.acquire_read()
try:
    # read section
    ...
finally:
    lock.release_read()

lock.acquire_write()
try:
    # write section
    ...
finally:
    lock.release_write()
```

## API Reference

### Class `ReadWriteLock`
#### Constructor
- `__init__()`: Initialize internal condition and reader counter.

#### Methods
- `acquire_read()`: Acquire a shared read lock (increments reader count).
- `release_read()`: Release the shared read lock (decrements reader count; notifies writers when zero).
- `acquire_write()`: Acquire an exclusive write lock (blocks until no readers are active).
- `release_write()`: Release the exclusive write lock.

#### Context Managers
- `read_lock()`: Context manager for read access.
- `write_lock()`: Context manager for write access.

## Thread Safety Details
- Built on `threading.Condition` with an internal mutex.
- Reader count tracks active readers.
- Writers block while the reader count > 0.
- `notify_all()` is used to wake waiting writers when the last reader releases.

## Performance
Benchmark tests using `pytest-benchmark` are provided in the `tests/` folder to measure:
- `acquire_read()` / `release_read()` performance.
- `acquire_write()` / `release_write()` performance.

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
├── run_tests.sh
└── LICENSE
```

## Running Tests
Ensure test dependencies are installed (see `requirements.txt`), then run:

```bash
pytest
```

HTML reports will be generated under the `reports/` directory.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/foo`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature/foo`).
5. Open a Pull Request.

Ensure all tests pass before submitting.

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Authors
- **Mogduz** — initial author and maintainer
