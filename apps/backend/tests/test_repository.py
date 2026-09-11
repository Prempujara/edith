"""Tests for the TaskRepository boundary and the in-memory store (M2.1).

Covers: repository Protocol conformance, per-task monotonic event sequencing,
thread-safe concurrent mutations, and bounded (family-aware) retention.
"""

from __future__ import annotations

import threading

from runtime.repository import TaskRepository
from runtime.store import TaskStore
from schemas.enums import EventType, TaskStatus
from schemas.event import Event
from schemas.task import Task


def _task(status: TaskStatus = TaskStatus.CREATED, parent: str | None = None) -> Task:
    return Task(requester="user", input="x", status=status, parent_task_id=parent)


# --- repository boundary -----------------------------------------------
def test_task_store_satisfies_repository_protocol():
    # Structural (runtime_checkable) conformance: the Runtime depends on this
    # interface, not the concrete class.
    assert isinstance(TaskStore(), TaskRepository)


def test_repository_roundtrip():
    store = TaskStore()
    t = _task()
    store.add(t)
    assert store.get(t.id) is t          # live object handed back
    assert store.list_tasks() == [t]
    assert store.get("missing") is None
    assert store.get_events("missing") == []


# --- event sequencing --------------------------------------------------
def test_event_seq_is_per_task_monotonic():
    store = TaskStore()
    a, b = _task(), _task()
    store.add(a)
    store.add(b)

    e1 = store.add_event(Event(task_id=a.id, type=EventType.TASK_CREATED))
    e2 = store.add_event(Event(task_id=a.id, type=EventType.TASK_QUEUED))
    f1 = store.add_event(Event(task_id=b.id, type=EventType.TASK_CREATED))

    # Sequence is per-task and 1-based: each stream numbers independently.
    assert e1.seq == 1 and e2.seq == 2
    assert f1.seq == 1
    assert [e.seq for e in store.get_events(a.id)] == [1, 2]
    assert [e.seq for e in store.get_events(b.id)] == [1]


def test_get_events_returns_ascending_seq_order():
    store = TaskStore()
    t = _task()
    store.add(t)
    for _ in range(5):
        store.add_event(Event(task_id=t.id, type=EventType.TOOL_STARTED))
    seqs = [e.seq for e in store.get_events(t.id)]
    assert seqs == [1, 2, 3, 4, 5]


# --- thread safety -----------------------------------------------------
def test_concurrent_event_appends_have_unique_contiguous_seqs():
    store = TaskStore()
    t = _task()
    store.add(t)

    n_threads, per_thread = 8, 100
    barrier = threading.Barrier(n_threads)

    def worker() -> None:
        barrier.wait()  # maximise contention
        for _ in range(per_thread):
            store.add_event(Event(task_id=t.id, type=EventType.TOOL_STARTED))

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    events = store.get_events(t.id)
    total = n_threads * per_thread
    # Nothing lost or overwritten, and seqs form a contiguous 1..N set.
    assert len(events) == total
    assert sorted(e.seq for e in events) == list(range(1, total + 1))


def test_concurrent_task_adds_all_present():
    store = TaskStore()
    n_threads, per_thread = 8, 50
    barrier = threading.Barrier(n_threads)

    def worker() -> None:
        barrier.wait()
        for _ in range(per_thread):
            store.add(_task())

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    assert len(store.list_tasks()) == n_threads * per_thread


# --- bounded retention -------------------------------------------------
def test_retention_unbounded_by_default():
    store = TaskStore()  # max_tasks=None
    for _ in range(50):
        store.add(_task(TaskStatus.COMPLETED))
    assert len(store.list_tasks()) == 50


def test_retention_never_evicts_active_tasks():
    store = TaskStore(max_tasks=1)
    active = [_task(), _task(), _task()]  # all CREATED (non-terminal)
    for t in active:
        store.add(t)
    # All retained despite exceeding the limit: active tasks are never dropped.
    assert {t.id for t in store.list_tasks()} == {t.id for t in active}


def test_retention_evicts_oldest_terminal_first():
    store = TaskStore(max_tasks=2)
    a = _task(TaskStatus.COMPLETED)
    b = _task(TaskStatus.COMPLETED)
    store.add(a)
    store.add(b)
    store.add_event(Event(task_id=a.id, type=EventType.TASK_COMPLETED))
    c = _task(TaskStatus.CREATED)
    store.add(c)  # over limit -> evict oldest terminal (a), then stop at limit

    ids = {t.id for t in store.list_tasks()}
    assert a.id not in ids
    assert ids == {b.id, c.id}
    assert store.get_events(a.id) == []  # events cleaned up with the task


def test_retention_evicts_whole_family_together():
    store = TaskStore(max_tasks=2)
    parent = _task(TaskStatus.COMPLETED)
    child = _task(TaskStatus.COMPLETED, parent=parent.id)
    store.add(parent)
    store.add(child)                       # len 2 (at limit)
    newest = _task(TaskStatus.CREATED)
    store.add(newest)                      # over limit -> evict the parent+child family

    ids = {t.id for t in store.list_tasks()}
    assert parent.id not in ids and child.id not in ids
    assert ids == {newest.id}
    assert store.get_events(parent.id) == []
    assert store.get_events(child.id) == []


def test_retention_keeps_family_with_active_child():
    store = TaskStore(max_tasks=1)
    parent = _task(TaskStatus.COMPLETED)
    child = _task(TaskStatus.RUNNING, parent=parent.id)  # child still active
    newest = _task(TaskStatus.CREATED)
    store.add(parent)
    store.add(child)
    store.add(newest)
    # Nothing is evictable: the terminal parent's family has an active child,
    # and the other tasks are active. Consistency over the limit.
    assert {t.id for t in store.list_tasks()} == {parent.id, child.id, newest.id}
