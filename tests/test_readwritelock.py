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
- pytest-xdist (xdist) for parallel test execution
- pytest-asyncio for asynchronous tests
- pytest-benchmark for performance benchmarking
- pytest-html for HTML report generation
"""

import os
import datetime
import pytest
import threading
import time
import asyncio
import random
from readwritelock.readwritelock import ReadWriteLock

# Configure pytest-html to output reports named with current date and time

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

    def reader_thread():
        with lock.read_lock():
            start.wait()
            end.wait()

    threads = [threading.Thread(target=reader_thread) for _ in range(readers)]
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

    def reader_func():
        with lock.read_lock():
            r_started.set()
            r_release.wait()

    t_reader = threading.Thread(target=reader_func)
    t_reader.start()
    r_started.wait()

    def writer_func():
        with lock.write_lock():
            w_acquired.set()

    t_writer = threading.Thread(target=writer_func)
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

    def writer_func():
        with lock.write_lock():
            w_started.set()
            w_release.wait()

    t_writer = threading.Thread(target=writer_func)
    t_writer.start()
    w_started.wait()

    def reader_func():
        with lock.read_lock():
            r_acquired.set()

    t_reader = threading.Thread(target=reader_func)
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

# --- Benchmark tests ---

def test_benchmark_read_lock(benchmark, lock):
    """
    Benchmark acquire/release read lock performance.
    """
    def acquire_release():
        lock.acquire_read()
        lock.release_read()
    benchmark(acquire_release)


def test_benchmark_write_lock(benchmark, lock):
    """
    Benchmark acquire/release write lock performance.
    """
    def acquire_release():
        lock.acquire_write()
        lock.release_write()
    benchmark(acquire_release)

# --- Upgrade/Downgrade Scenarios ---

def test_upgrade_reader_to_writer_deadlock(lock):
    """
    Test that a thread holding a read lock and then attempting to upgrade to a write lock deadlocks.

    A thread that calls acquire_read() and then acquire_write() without releasing the read lock should block forever (deadlock).
    """
    r_started = threading.Event()

    def upgrade():
        lock.acquire_read()
        r_started.set()
        lock.acquire_write()

    t = threading.Thread(target=upgrade, daemon=True)
    t.start()
    assert r_started.wait(timeout=1)
    time.sleep(0.1)
    assert t.is_alive()


def test_downgrade_writer_to_reader(lock):
    """
    Test downgrade from writer to reader lock in same thread.

    After releasing a write lock, acquiring a read lock should succeed immediately.
    """
    with lock.write_lock():
        pass
    with lock.read_lock():
        pass

# --- Mass Reader Access with Intermittent Writer ---

def test_mass_readers_with_writer_update(lock):
    """
    Test mass concurrent read access with a writer updating the shared value in between.

    Spawns multiple reader threads to read a shared resource before and after a writer thread updates it.
    Ensures some readers observe the old value and some observe the new value, demonstrating proper lock behavior.
    """
    class Shared:
        def __init__(self):
            self.value = 0

    shared = Shared()
    values = []
    values_lock = threading.Lock()

    def reader():
        with lock.read_lock():
            val = shared.value
        with values_lock:
            values.append(val)

    def writer():
        with lock.write_lock():
            shared.value = 1

    readers1 = [threading.Thread(target=reader) for _ in range(5)]
    for t in readers1:
        t.start()
    for t in readers1:
        t.join()

    writer_thread = threading.Thread(target=writer)
    writer_thread.start()
    writer_thread.join()

    readers2 = [threading.Thread(target=reader) for _ in range(5)]
    for t in readers2:
        t.start()
    for t in readers2:
        t.join()

    assert 0 in values and 1 in values

# --- Stress Test ---

def test_stress_concurrent_read_write(lock):
    """
    Stress test for concurrent read and write operations under high load.

    Spawns multiple reader and writer threads performing many lock operations to ensure no deadlocks and correct final state.
    """
    num_readers = 50
    num_writers = 10
    iterations_read = 100
    iterations_write = 20

    def reader_worker():
        for _ in range(iterations_read):
            with lock.read_lock():
                # simulate read workload
                pass

    def writer_worker():
        for _ in range(iterations_write):
            with lock.write_lock():
                # simulate write workload
                pass

    threads = [threading.Thread(target=reader_worker) for _ in range(num_readers)] + [threading.Thread(target=writer_worker) for _ in range(num_writers)]
    random.shuffle(threads)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # After stress test, there should be no active readers
    assert lock._readers == 0
