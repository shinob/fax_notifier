
import pytest

from fax_notifier.database import (
    get_all_faxes,
    get_new_faxes,
    init_db,
    insert_fax,
    mark_notified,
)


@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


def test_insert_fax(db):
    record_id = insert_fax("/tmp/fax001.pdf", db_path=db)
    assert record_id is not None
    assert record_id > 0


def test_insert_fax_duplicate(db):
    insert_fax("/tmp/fax001.pdf", db_path=db)
    result = insert_fax("/tmp/fax001.pdf", db_path=db)
    assert result is None


def test_get_all_faxes(db):
    insert_fax("/tmp/a.pdf", db_path=db)
    insert_fax("/tmp/b.pdf", db_path=db)
    faxes = get_all_faxes(db_path=db)
    assert len(faxes) == 2


def test_mark_notified(db):
    record_id = insert_fax("/tmp/fax001.pdf", db_path=db)
    mark_notified(record_id, db_path=db)
    faxes = get_all_faxes(db_path=db)
    assert faxes[0]["notified"] == 1
    assert faxes[0]["notified_at"] is not None


def test_get_new_faxes(db):

    insert_fax("/tmp/old.pdf", db_path=db)
    faxes = get_all_faxes(db_path=db)
    since = faxes[0]["received_at"]

    insert_fax("/tmp/new.pdf", db_path=db)
    new = get_new_faxes(since, db_path=db)
    assert len(new) == 1
    assert new[0]["filename"] == "new.pdf"
