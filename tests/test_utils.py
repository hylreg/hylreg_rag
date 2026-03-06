from src.utils.utils import create_sample_docs_folder, validate_file_path


def test_create_sample_docs_folder_creates_text_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    create_sample_docs_folder()

    sample_dir = tmp_path / "sample_docs"
    assert sample_dir.exists()
    assert (sample_dir / "company_info.txt").exists()
    assert (sample_dir / "company_overview.txt").exists()
    assert (sample_dir / "services.txt").exists()


def test_validate_file_path_for_supported_file_types(tmp_path):
    txt_file = tmp_path / "a.txt"
    txt_file.write_text("content", encoding="utf-8")
    assert validate_file_path(str(txt_file))

    invalid_file = tmp_path / "a.md"
    invalid_file.write_text("content", encoding="utf-8")
    assert not validate_file_path(str(invalid_file))


def test_validate_file_path_for_directory(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    assert not validate_file_path(str(docs))

    (docs / "readme.txt").write_text("ok", encoding="utf-8")
    assert validate_file_path(str(docs))
