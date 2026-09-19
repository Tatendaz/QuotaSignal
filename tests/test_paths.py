from quotasignal import paths


def test_user_dir_copies_legacy_settings_once(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    legacy = tmp_path / paths.LEGACY_DIR
    legacy.mkdir()
    (legacy / "preferences.json").write_text('{"show_icon": true}')

    current = paths.user_dir("XDG_CONFIG_HOME", ".config")

    assert current == tmp_path / paths.APP_DIR
    assert (current / "preferences.json").read_text() == '{"show_icon": true}'
    assert (legacy / "preferences.json").exists()

    (current / "preferences.json").write_text("{}")
    paths.user_dir("XDG_CONFIG_HOME", ".config")
    assert (current / "preferences.json").read_text() == "{}"


def test_user_dir_without_legacy_creates_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))

    current = paths.user_dir("XDG_CACHE_HOME", ".cache")

    assert current == tmp_path / paths.APP_DIR
    assert not current.exists()
