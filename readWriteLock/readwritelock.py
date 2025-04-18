"""
readwritelock.py - Reader-Writer Lock Implementation

This module provides the ReadWriteLock class, which allows multiple threads to
safely perform concurrent read operations or a single thread to perform exclusive
write operations. It uses a Condition variable internally to manage readers and
writers without starvation.

Classes:
    ReadWriteLock: A lock object supporting multiple concurrent readers or one
    exclusive writer.

Usage:
    from readwritelock import ReadWriteLock

    lock = ReadWriteLock()
    # Shared read
    with lock.read_lock():
        # perform thread-safe read operations
        pass

    # Exclusive write
    with lock.write_lock():
        # perform thread-safe write operations
        pass

Author:
    Modguz

Date:
    2025-04-18
"""

from contextlib import contextmanager
from threading import Lock, Condition

class ReadWriteLock:
    """
    Reader-Writer Lock.

    Allows multiple threads to concurrently acquire a shared read lock,
    or a single thread to acquire an exclusive write lock.
    """

    def __init__(self) -> None:
        """
        Initialize a new ReadWriteLock instance.

        Sets up the internal Condition object for thread synchronization
        and initializes the count of active readers to zero.
        """
        self._condition = Condition(Lock())
        self._readers = 0

    def acquire_read(self) -> None:
        """
        Acquire a shared read lock.

        Increments the internal reader count, indicating that a thread
        is performing a read operation. Multiple threads can hold the
        read lock simultaneously. Writers will block until all readers
        have released their locks.
        """
        with self._condition:
            self._readers += 1

    def release_read(self) -> None:
        """
        Release a shared read lock.

        Decrements the internal reader count. When the reader count
        reaches zero, notifies waiting writers that they may proceed.
        """
        with self._condition:
            self._readers -= 1
            if self._readers == 0:
                # Notify all waiting threads (particularly writers)
                self._condition.notify_all()

    def acquire_write(self) -> None:
        """
        Acquire an exclusive write lock.

        Blocks until there are no active readers. Once acquired, the
        calling thread holds the lock exclusively, preventing other
        readers or writers from entering the critical section.

        Raises:
            RuntimeError: If unable to acquire the write lock due to an error.
        """
        self._condition.acquire()
        try:
            while self._readers > 0:
                self._condition.wait()
        except Exception:
            # Ensure lock is released on exception!
            self._condition.release()
            raise

    def release_write(self) -> None:
        """
        Release the exclusive write lock.

        Releases the internal lock, allowing other readers or writers
        to acquire their respective locks.
        """
        self._condition.release()

    @contextmanager
    def read_lock(self):
        """
        Context manager for a shared read lock.

        Usage:
            with lock.read_lock():
                # perform read operations here

        Guarantees that acquire_read() is called before entering
        the block and release_read() is called upon exit,
        even if an exception occurs.
        """
        self.acquire_read()
        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self):
        """
        Context manager for an exclusive write lock.

        Usage:
            with lock.write_lock():
                # perform write operations here

        Guarantees that acquire_write() is called before entering
        the block and release_write() is called upon exit,
        even if an exception occurs.
        """
        self.acquire_write()
        try:
            yield
        finally:
            self.release_write()
