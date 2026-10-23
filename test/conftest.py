import os
from pathlib import Path

import pytest

os.environ.setdefault("CARGO_DRONE_DB", ":memory:")


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("CARGO_DRONE_DB", str(db_file))
    # Reload config agar DB_PATH ikut berubah
    import importlib
    import config
    importlib.reload(config)
    yield db_file