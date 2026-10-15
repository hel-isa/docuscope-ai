import sqlite3

import pytest

from app.storage.sqlite_store import init_db, save_fingerprint


@pytest.mark.parametrize(
    "operation",
    [init_db, lambda db_path: save_fingerprint(db_path, None)],
)
def test_database_connections_close_when_setup_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path, operation
) -> None:
    class FailingConnection:
        closed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def cursor(self):
            raise sqlite3.OperationalError("forced failure")

        def close(self) -> None:
            self.closed = True

    connection = FailingConnection()
    monkeypatch.setattr(sqlite3, "connect", lambda _path: connection)

    with pytest.raises(sqlite3.OperationalError, match="forced failure"):
        operation(tmp_path / "test.db")

    assert connection.closed
