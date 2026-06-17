from __future__ import annotations

import threading
import time

from fax_notifier.watcher import wait_until_stable


def test_wait_until_stable_already_stable(tmp_path):
    filepath = tmp_path / "fax.pdf"
    filepath.write_bytes(b"x" * 100)

    assert wait_until_stable(str(filepath), interval=0.05, required_checks=2, timeout=1)


def test_wait_until_stable_waits_for_growth_to_stop(tmp_path):
    filepath = tmp_path / "fax.pdf"
    filepath.write_bytes(b"x")

    def grow():
        for _ in range(3):
            time.sleep(0.05)
            with open(filepath, "ab") as f:
                f.write(b"x" * 50)

    threading.Thread(target=grow, daemon=True).start()

    assert wait_until_stable(str(filepath), interval=0.05, required_checks=2, timeout=2)


def test_wait_until_stable_times_out_if_never_stable(tmp_path):
    filepath = tmp_path / "fax.pdf"
    filepath.write_bytes(b"x")
    stop = threading.Event()

    def keep_growing():
        while not stop.is_set():
            time.sleep(0.02)
            with open(filepath, "ab") as f:
                f.write(b"x")

    t = threading.Thread(target=keep_growing, daemon=True)
    t.start()
    try:
        assert not wait_until_stable(
            str(filepath), interval=0.05, required_checks=2, timeout=0.3
        )
    finally:
        stop.set()
        t.join()
