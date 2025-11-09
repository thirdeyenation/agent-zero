from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from python.helpers.files import (
    OUTPUT_MODE_STRING,
    SORT_ASC,
    SORT_BY_NAME,
    create_dir,
    delete_dir,
    file_tree,
    get_abs_path,
    write_file,
)


@contextmanager
def _project_directory(relative_path: str):
    delete_dir(relative_path)
    try:
        create_dir(relative_path)
        yield Path(get_abs_path(relative_path))
    finally:
        delete_dir(relative_path)


def _materialize_structure(base_rel: str) -> None:
    write_file(os.path.join(base_rel, "file.txt"), "content")


def test_file_tree_invalid_sort_key() -> None:
    base_rel = "tmp/tests/file_tree/invalid_sort_key"
    with _project_directory(base_rel):
        _materialize_structure(base_rel)
        with pytest.raises(ValueError):
            file_tree(
                base_rel,
                sort=("unsupported", SORT_ASC),
                output_mode=OUTPUT_MODE_STRING,
            )


def test_file_tree_invalid_sort_direction() -> None:
    base_rel = "tmp/tests/file_tree/invalid_sort_direction"
    with _project_directory(base_rel):
        _materialize_structure(base_rel)
        with pytest.raises(ValueError):
            file_tree(
                base_rel,
                sort=(SORT_BY_NAME, "ascending"),
                output_mode=OUTPUT_MODE_STRING,
            )


def test_file_tree_invalid_output_mode() -> None:
    base_rel = "tmp/tests/file_tree/invalid_output_mode"
    with _project_directory(base_rel):
        _materialize_structure(base_rel)
        with pytest.raises(ValueError):
            file_tree(base_rel, output_mode="yaml")


def test_file_tree_negative_depth_and_lines() -> None:
    base_rel = "tmp/tests/file_tree/invalid_depth_lines"
    with _project_directory(base_rel):
        _materialize_structure(base_rel)
        with pytest.raises(ValueError):
            file_tree(base_rel, max_depth=-1)
        with pytest.raises(ValueError):
            file_tree(base_rel, max_lines=-5)


def test_file_tree_missing_ignore_file() -> None:
    base_rel = "tmp/tests/file_tree/missing_ignore"
    with _project_directory(base_rel):
        _materialize_structure(base_rel)
        with pytest.raises(FileNotFoundError):
            file_tree(
                base_rel,
                ignore="file:missing.ignore",
                output_mode=OUTPUT_MODE_STRING,
            )
