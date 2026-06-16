from __future__ import annotations

import io
import os
from typing import Optional

from flask import Flask, abort, jsonify, render_template, request, send_file

from ..config import AppConfig
from ..database import get_all_faxes, get_new_faxes

app = Flask(__name__)
_config: Optional[AppConfig] = None
_db_path: str = "fax_notifier.db"


def create_app(config: AppConfig, db_path: str = "fax_notifier.db") -> Flask:
    global _config, _db_path
    _config = config
    _db_path = db_path
    app.config["POLLING_INTERVAL"] = config.web.polling_interval
    return app


@app.route("/")
def index():
    polling_interval = app.config.get("POLLING_INTERVAL", 10)
    return render_template("index.html", polling_interval=polling_interval)


@app.route("/api/faxes")
def api_faxes():
    faxes = get_all_faxes(db_path=_db_path)
    return jsonify(faxes)


@app.route("/api/faxes/new")
def api_faxes_new():
    since = request.args.get("since", "")
    if not since:
        return jsonify([])
    faxes = get_new_faxes(since, db_path=_db_path)
    return jsonify(faxes)


@app.route("/api/faxes/<int:record_id>/pages")
def api_fax_pages(record_id: int):
    record = _get_record(record_id)
    filepath = record["filepath"]
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".tiff", ".tif"):
        return jsonify({"total": 1})

    from PIL import Image

    img = Image.open(filepath)
    total = 0
    try:
        while True:
            total += 1
            img.seek(total)
    except EOFError:
        pass
    return jsonify({"total": total})


@app.route("/api/faxes/<int:record_id>/file")
def api_fax_file(record_id: int):
    record = _get_record(record_id)
    filepath = record["filepath"]

    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".tiff", ".tif"):
        try:
            page = int(request.args.get("page", 0))
        except ValueError:
            page = 0
        return _serve_tiff_page_as_png(filepath, page)

    return send_file(filepath, mimetype="application/pdf")


def _get_record(record_id: int) -> dict:
    faxes = get_all_faxes(db_path=_db_path)
    record = next((f for f in faxes if f["id"] == record_id), None)
    if record is None:
        abort(404)
    if not os.path.exists(record["filepath"]):
        abort(404)
    return record


def _serve_tiff_page_as_png(filepath: str, page: int):
    from PIL import Image

    img = Image.open(filepath)
    try:
        img.seek(page)
    except EOFError:
        abort(404)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
