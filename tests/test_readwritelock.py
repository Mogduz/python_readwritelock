"""
test_readwritelock.py - Unit tests for ReadWriteLock class.

This module contains a suite of unit tests verifying the correctness,
thread-safety, and robustness of the ReadWriteLock implementation defined
in readwritelock.py.

Tests cover:
  - Context manager behavior for both read and write locks
  - Exception safety and proper lock release
  - Concurrency scenarios with multiple readers and writer-reader interactions
  - Edge cases such as releasing locks without prior acquisition and nested locks

Author: Modguz
Date: 2025-04-18
"""

import unittest
import threading
import time

from readwritelock_old import ReadWriteLock


class TestReadWriteLock(unittest.TestCase):
    """
    Unit test suite for the ReadWriteLock class.

    Verifies that the lock:
      - Allows multiple concurrent readers
      - Provides exclusive write access
      - Correctly handles context manager entry and exit
      - Properly releases locks on exceptions
      - Manages edge cases without deadlocks or undefined behavior
    """

    def test_read_lock_context_manager(self):
        """
        Verify context manager increments and decrements reader count.

        Functional flow:
          1. Create ReadWriteLock instance.
          2. Check initial readers == 0.
          3. Enter with read_lock():
             - acquire_read() increments readers to 1.
             - Assert readers == 1 inside block.
          4. Exit block:
             - release_read() decrements readers to 0.
          5. Assert readers == 0 after exit.
        """
        lock = ReadWriteLock()
        self.assertEqual(lock._readers, 0)
        with lock.read_lock():
            self.assertEqual(lock._readers, 1)
        self.assertEqual(lock._readers, 0)

    def test_write_lock_context_manager(self):
        """
        Verify write context manager provides exclusive access.

        Functional flow:
          1. Create ReadWriteLock instance.
          2. Enter with write_lock():
             - acquire_write() blocks until no readers, then locks.
             - Assert readers == 0 inside block.
          3. Exit block:
             - release_write() unlocks.
          4. Re-acquire write_lock() to ensure lock released properly.
        """
        lock = readWriteLock.ReadWriteLock()
        with lock.write_lock():
            self.assertEqual(lock._readers, 0)
        with lock.write_lock():
            pass

    def test_exception_in_read_lock(self):
        """
        Ensure exceptions inside read context still release lock.

        Functional flow:
          1. Create ReadWriteLock instance.
          2. Enter read_lock() and raise ValueError.
          3. Exception propagates out of context.
          4. release_read() in finally resets readers to 0.
        """
        lock = ReadWriteLock()
        with self.assertRaises(ValueError):
            with lock.read_lock():
                raise ValueError("error")
        self.assertEqual(lock._readers, 0)

    def test_exception_in_write_lock(self):
        """
        Ensure exceptions inside write context still release lock.

        Functional flow:
          1. Create ReadWriteLock instance.
          2. Enter write_lock() and raise ValueError.
          3. Exception propagates out of context.
          4. release_write() in finally frees lock.
          5. Subsequent write_lock() succeeds.
        """
        lock = ReadWriteLock()
        with self.assertRaises(ValueError):
            with lock.write_lock():
                raise ValueError("error")
        with lock.write_lock():
            pass

    def test_multiple_concurrent_readers(self):
        """
        Verify multiple threads can read concurrently.

        Functional flow:
          1. Create ReadWriteLock and barriers for 5 readers.
          2. Each reader thread enters read_lock(), waits at start barrier.
          3. After start barrier, assert readers == 5.
          4. Release readers via end barrier.
          5. After join, assert readers == 0.
        """
        lock = ReadWriteLock()
        readers = 5
        start = threading.Barrier(readers + 1)
        end = threading.Barrier(readers + 1)
        def rdr():
            with lock.read_lock():
                start.wait()
                end.wait()
        threads = [threading.Thread(target=rdr) for _ in range(readers)]
        for t in threads: t.start()
        start.wait()
        self.assertEqual(lock._readers, readers)
        end.wait()
        for t in threads: t.join()
        self.assertEqual(lock._readers, 0)

    def test_writer_blocks_until_readers_finish(self):
        """
        Verify writer waits for readers to finish.

        Functional flow:
          1. Start reader that holds lock until event.
          2. Attempt writer in another thread.
          3. Sleep and assert writer not acquired.
          4. Release reader and join writer thread.
          5. Assert writer acquired.
        """
        lock = ReadWriteLock()
        r_started = threading.Event()
        r_release = threading.Event()
        w_acquired = threading.Event()
        def rdr():
            with lock.read_lock():
                r_started.set(); r_release.wait()
        threading.Thread(target=rdr).start(); r_started.wait()
        def wtr():
            with lock.write_lock(): w_acquired.set()
        wt = threading.Thread(target=wtr); wt.start(); time.sleep(0.1)
        self.assertFalse(w_acquired.is_set())
        r_release.set(); wt.join()
        self.assertTrue(w_acquired.is_set())

    def test_readers_block_when_writer_active(self):
        """
        Verify readers block while writer active.

        Functional flow:
          1. Start writer that holds lock until event.
          2. Attempt reader in another thread.
          3. Sleep and assert reader not acquired.
          4. Release writer and join reader thread.
          5. Assert reader acquired.
        """
        lock = ReadWriteLock()
        w_started = threading.Event()
        w_release = threading.Event()
        r_acquired = threading.Event()
        def wtr():
            with lock.write_lock(): w_started.set(); w_release.wait()
        threading.Thread(target=wtr).start(); w_started.wait()
        def rdr2():
            with lock.read_lock(): r_acquired.set()
        rt = threading.Thread(target=rdr2); rt.start(); time.sleep(0.1)
        self.assertFalse(r_acquired.is_set())
        w_release.set(); rt.join()
        self.assertTrue(r_acquired.is_set())

    def test_nested_read_locks(self):
        """
        Verify nested reads increment readers cumulatively.

        Functional flow:
          1. Enter two nested read_lock() contexts.
          2. Assert readers == 2 inside inner.
          3. Exit both contexts and assert readers == 0.
        """
        lock = ReadWriteLock()
        with lock.read_lock():
            with lock.read_lock(): self.assertEqual(lock._readers, 2)
        self.assertEqual(lock._readers, 0)

    # Additional edge-case tests

    def test_release_read_without_acquire(self):
        """
        Verify release_read underflows readers count.

        Functional flow:
          1. Record initial readers.
          2. Call release_read() without acquire_read().
          3. Assert readers == initial - 1.
        """
        lock = ReadWriteLock()
        init = lock._readers; lock.release_read()
        self.assertEqual(lock._readers, init - 1)

    def test_release_write_without_acquire(self):
        """
        Verify release_write without acquire_write raises.

        Functional flow:
          1. Call release_write() unheld.
          2. Expect RuntimeError.
        """
        lock = ReadWriteLock()
        with self.assertRaises(RuntimeError): lock.release_write()

    def test_nested_write_locks_block(self):
        """
        Verify write_lock non-reentrant behavior.

        Functional flow:
          1. First write_lock acquired.
          2. Attempt nested write_lock() should block.
          3. Join thread with timeout and assert thread alive.
        """
        lock = ReadWriteLock()
        def nest():
            with lock.write_lock():
                with lock.write_lock(): pass
        t = threading.Thread(target=nest, daemon=True)
        t.start(); t.join(timeout=0.1)
        self.assertTrue(t.is_alive())

if __name__ == '__main__': unittest.main()
