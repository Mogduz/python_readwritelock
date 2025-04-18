pytest_plugins = [
    "pytest_cov",
    "pytest_mock",
    "xdist",
    "pytest_asyncio",
    "pytest_benchmark",
    "pytest_html",
]

"""
Test suite for ReadWriteLock class from python_readwritelock repository.

Plugins:
- pytest-cov for coverage measurement
- pytest-mock for mocking and patching
- pytest-xdist for parallel test execution
- pytest-asyncio for asynchronous tests
- pytest-benchmark for performance benchmarking
- pytest-html for HTML report generation
- pytest-sugar for nicer CLI output
- pytest-randomly for random test ordering
"""

import os
import datetime
import pytest
import threading
import time
import asyncio
from readwritelock.readwritelock import ReadWriteLock

# Configure pytest-html to output reports named with current date and time

def pytest_configure(config):
    if config.pluginmanager.hasplugin('html'):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(os.getcwd(), 'reports')
        os.makedirs(report_dir, exist_ok=True)
        config.option.htmlpath = os.path.join(report_dir, f"report_{now}.html")

@pytest.fixture
def lock():
    """
    Provides a fresh ReadWriteLock instance for tests.
    """
    return ReadWriteLock()

# --- Basic functionality tests ---

def test_read_lock_context_manager(lock):
    """
    Verify context manager increments and decrements reader count.
    """
    assert lock._readers == 0
    with lock.read_lock():
        assert lock._readers == 1
    assert lock._readers == 0


def test_write_lock_context_manager(lock):
    """
    Verify write context manager provides exclusive access.
    """
    assert lock._readers == 0
    with lock.write_lock():
        assert lock._readers == 0
    # Ensure lock is released by reacquiring
    with lock.write_lock():
        pass

# --- Exception safety tests ---

def test_exception_in_read_lock(lock):
    """
    Exceptions inside read context still release lock.
    """
    with pytest.raises(ValueError):
        with lock.read_lock():
            raise ValueError("error")
    assert lock._readers == 0


def test_exception_in_write_lock(lock):
    """
    Exceptions inside write context still release lock.
    """
    with pytest.raises(ValueError):
        with lock.write_lock():
            raise ValueError("error")
    # Subsequent acquisition should succeed
    with lock.write_lock():
        pass

# --- Concurrency tests ---

def test_multiple_concurrent_readers(lock):
    """
    Verify multiple threads can read concurrently.
    """
    readers = 5
    start = threading.Barrier(readers + 1)
    end = threading.Barrier(readers + 1)

    def reader():
        with lock.read_lock():
            start.wait()
            end.wait()

    threads = [threading.Thread(target=reader) for _ in range(readers)]
    for t in threads:
        t.start()
    start.wait()
    assert lock._readers == readers
    end.wait()
    for t in threads:
        t.join()
    assert lock._readers == 0


def test_writer_blocks_until_readers_finish(lock):
    """
    Verify writer waits for readers to finish.
    """
    r_started = threading.Event()
    r_release = threading.Event()
    w_acquired = threading.Event()

    def reader():
        with lock.read_lock():
            r_started.set()
            r_release.wait()

    t_reader = threading.Thread(target=reader)
    t_reader.start()
    r_started.wait()

    def writer():
        with lock.write_lock():
            w_acquired.set()

    t_writer = threading.Thread(target=writer)
    t_writer.start()
    time.sleep(0.1)
    assert not w_acquired.is_set()
    r_release.set()
    t_writer.join()
    assert w_acquired.is_set()
    t_reader.join()


def test_readers_block_when_writer_active(lock):
    """
    Verify readers block while writer is active.
    """
    w_started = threading.Event()
    w_release = threading.Event()
    r_acquired = threading.Event()

    def writer():
        with lock.write_lock():
            w_started.set()
            w_release.wait()

    t_writer = threading.Thread(target=writer)
    t_writer.start()
    w_started.wait()

    def reader():
        with lock.read_lock():
            r_acquired.set()

    t_reader = threading.Thread(target=reader)
    t_reader.start()
    time.sleep(0.1)
    assert not r_acquired.is_set()
    w_release.set()
    t_reader.join()
    assert r_acquired.is_set()
    t_writer.join()

# --- Nested and edge-case tests ---

def test_nested_read_locks(lock):
    """
    Verify nested reads increment readers cumulatively.
    """
    with lock.read_lock():
        with lock.read_lock():
            assert lock._readers == 2
    assert lock._readers == 0


def test_release_read_without_acquire(lock):
    """
    Verify release_read underflows readers count.
    """
    init = lock._readers
    lock.release_read()
    assert lock._readers == init - 1


def test_release_write_without_acquire(lock):
    """
    Verify release_write without acquire_write raises RuntimeError.
    """
    with pytest.raises(RuntimeError):
        lock.release_write()


def test_nested_write_locks_block(lock):
    """
    Verify write_lock non-reentrant behavior.
    """
    def nested():
        with lock.write_lock():
            with lock.write_lock():
                pass

    t = threading.Thread(target=nested, daemon=True)
    t.start()
    t.join(timeout=0.1)
    assert t.is_alive()

# --- Async test example ---

@pytest.mark.asyncio
async def test_async_read_lock(lock):
    """
    Example async test acquiring and releasing a read lock.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: lock.acquire_read())
    lock.release_read()
    assert lock._readers == 0

# --- Benchmark test ---

def test_benchmark_read_lock(benchmark, lock):
    """
    Benchmark acquire/release read lock performance.
    """
    def acquire_release():
        lock.acquire_read()
        lock.release_read()
    benchmark(acquire_release)
