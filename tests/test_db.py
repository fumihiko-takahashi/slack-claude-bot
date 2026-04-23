import os
import tempfile

import pytest

from slack_claude_bot import SessionDB


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    d = SessionDB(db_path=path)
    d.init()
    yield d
    os.unlink(path)


def test_session_roundtrip(db):
    db.save_session("ts1", "sess-abc", "C123")
    assert db.get_session("ts1") == "sess-abc"


def test_session_update(db):
    db.save_session("ts1", "sess-abc", "C123")
    db.save_session("ts1", "sess-xyz", "C123")
    assert db.get_session("ts1") == "sess-xyz"


def test_unknown_session(db):
    assert db.get_session("unknown") is None


def test_lock_acquire_and_release(db):
    assert db.acquire_lock("ts1") is True
    assert db.acquire_lock("ts1") is False  # 二重取得は失敗
    db.release_lock("ts1")
    assert db.acquire_lock("ts1") is True  # 解放後は再取得できる


def test_clear_all_locks(db):
    db.acquire_lock("ts1")
    db.acquire_lock("ts2")
    db.clear_all_locks()
    assert db.acquire_lock("ts1") is True
    assert db.acquire_lock("ts2") is True
