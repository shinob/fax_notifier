
import pytest

from fax_notifier.config import AppConfig
from fax_notifier.database import init_db, insert_fax
from fax_notifier.web.app import create_app


@pytest.fixture
def app(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    config = AppConfig(watch_directory=str(tmp_path))
    flask_app = create_app(config, db_path=db_path)
    flask_app.config["TESTING"] = True
    return flask_app, db_path, tmp_path


@pytest.fixture
def client(app):
    flask_app, db_path, tmp_path = app
    return flask_app.test_client(), db_path, tmp_path


def _make_single_tiff(path):
    """1ページの最小TIFFファイルを作成する。"""
    from PIL import Image

    img = Image.new("RGB", (10, 10), color=(255, 255, 255))
    img.save(path, format="TIFF")


def _make_multi_tiff(path, pages: int):
    """複数ページのTIFFファイルを作成する。"""
    from PIL import Image

    imgs = [Image.new("RGB", (10, 10), color=(i * 40, 0, 0)) for i in range(pages)]
    imgs[0].save(path, format="TIFF", save_all=True, append_images=imgs[1:])


def test_api_faxes_empty(client):
    c, db_path, tmp_path = client
    res = c.get("/api/faxes")
    assert res.status_code == 200
    assert res.get_json() == []


def test_api_faxes_returns_records(client):
    c, db_path, tmp_path = client
    p = tmp_path / "fax001.pdf"
    p.write_bytes(b"%PDF-1.4")
    insert_fax(str(p), db_path=db_path)

    res = c.get("/api/faxes")
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["filename"] == "fax001.pdf"


def test_api_pages_single_tiff(client):
    c, db_path, tmp_path = client
    p = tmp_path / "fax.tiff"
    _make_single_tiff(str(p))
    insert_fax(str(p), db_path=db_path)

    faxes = c.get("/api/faxes").get_json()
    res = c.get(f"/api/faxes/{faxes[0]['id']}/pages")
    assert res.status_code == 200
    assert res.get_json()["total"] == 1


def test_api_pages_multi_tiff(client):
    c, db_path, tmp_path = client
    p = tmp_path / "fax_multi.tiff"
    _make_multi_tiff(str(p), pages=3)
    insert_fax(str(p), db_path=db_path)

    faxes = c.get("/api/faxes").get_json()
    res = c.get(f"/api/faxes/{faxes[0]['id']}/pages")
    assert res.status_code == 200
    assert res.get_json()["total"] == 3


def test_api_file_tiff_page(client):
    c, db_path, tmp_path = client
    p = tmp_path / "fax_multi.tiff"
    _make_multi_tiff(str(p), pages=3)
    insert_fax(str(p), db_path=db_path)

    faxes = c.get("/api/faxes").get_json()
    fax_id = faxes[0]["id"]

    for page in range(3):
        res = c.get(f"/api/faxes/{fax_id}/file?page={page}")
        assert res.status_code == 200
        assert res.content_type == "image/png"


def test_api_file_tiff_page_out_of_range(client):
    c, db_path, tmp_path = client
    p = tmp_path / "fax.tiff"
    _make_single_tiff(str(p))
    insert_fax(str(p), db_path=db_path)

    faxes = c.get("/api/faxes").get_json()
    res = c.get(f"/api/faxes/{faxes[0]['id']}/file?page=99")
    assert res.status_code == 404
