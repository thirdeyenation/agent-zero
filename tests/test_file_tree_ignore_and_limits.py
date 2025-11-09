from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path

import pytest

from python.helpers.files import (
    OUTPUT_MODE_FLAT,
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


def _materialize_structure(base_rel: str, structure: dict[str, object]) -> None:
    for name, value in structure.items():
        rel = os.path.join(base_rel, name)
        if isinstance(value, dict):
            create_dir(rel)
            _materialize_structure(rel, value)
        else:
            write_file(rel, "" if value is None else str(value))


def test_file_tree_ignore_file_reference_variants() -> None:
    base_rel = "tmp/tests/file_tree/ignore_file_variants"
    absolute_ignore = Path(get_abs_path(base_rel)) / "absolute.ignore"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "app": {
                    "build.tmp": "",
                    "main.py": "",
                    "README.md": "",
                },
            },
        )
        root_ignore = Path(get_abs_path(base_rel)) / ".treeignore"
        root_ignore.write_text("*.tmp\n", encoding="utf-8")
        absolute_ignore.write_text("README.md\n", encoding="utf-8")

        inline_result = file_tree(
            base_rel,
            ignore="file:.treeignore",
            output_mode=OUTPUT_MODE_FLAT,
        )
        abs_result = file_tree(
            base_rel,
            ignore=f"file:{absolute_ignore}",
            output_mode=OUTPUT_MODE_FLAT,
        )
        url_result = file_tree(
            base_rel,
            ignore="file://.treeignore",
            output_mode=OUTPUT_MODE_FLAT,
        )
        inline_patterns = file_tree(
            base_rel,
            ignore="*.tmp\n!build.tmp",
            output_mode=OUTPUT_MODE_FLAT,
        )

    inline_names = {item["name"] for item in inline_result}
    abs_names = {item["name"] for item in abs_result}
    url_names = {item["name"] for item in url_result}
    inline_pattern_names = {item["name"] for item in inline_patterns}

    assert "build.tmp" not in inline_names
    assert "README.md" in inline_names
    assert "README.md" not in abs_names
    assert inline_names == url_names
    assert "build.tmp" in inline_pattern_names


def test_file_tree_limits_emit_summary_comments() -> None:
    base_rel = "tmp/tests/file_tree/limits_summary"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "pkg": {
                    "a.py": "",
                    "b.py": "",
                    "c.py": "",
                    "d.py": "",
                    "e.py": "",
                    "dir1": {},
                    "dir2": {},
                    "dir3": {},
                    "dir4": {},
                }
            },
        )

        result = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            max_folders=2,
            max_files=2,
            output_mode=OUTPUT_MODE_STRING,
        )

    lines = result.splitlines()
    assert any("# 2 more folders" in line for line in lines)
    assert any("# 3 more files" in line for line in lines)


def test_file_tree_global_max_lines() -> None:
    base_rel = "tmp/tests/file_tree/global_max_lines"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dirA": {"a.txt": "", "b.txt": ""},
                "dirB": {"c.txt": "", "d.txt": ""},
                "x.txt": "",
                "y.txt": "",
            },
        )

        result = file_tree(
            base_rel,
            max_lines=5,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_STRING,
        )
        flat = file_tree(
            base_rel,
            max_lines=5,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_FLAT,
        )

    lines = result.splitlines()
    flat_levels = [item["level"] for item in flat]
    assert all(level <= 2 for level in flat_levels)
    top_level_names = {item["name"] for item in flat if item["level"] == 1}
    assert top_level_names == {"dirA", "dirB", "x.txt", "y.txt"}
    assert not any("│       " in line for line in lines)


def test_file_tree_limits_exact_counts_no_comment() -> None:
    base_rel = "tmp/tests/file_tree/limits_exact"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "pkg": {
                    "a.py": "",
                    "b.py": "",
                    "dir1": {},
                    "dir2": {},
                }
            },
        )

        result = file_tree(
            base_rel,
            folders_first=True,
            max_folders=2,
            max_files=2,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_STRING,
        )

    assert "# " not in result


def test_file_tree_limits_single_overflow_flat_mode() -> None:
    base_rel = "tmp/tests/file_tree/limits_single_flat"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "pkg": {
                    "dir_a": {},
                    "dir_b": {},
                }
            },
        )

        flat = file_tree(
            base_rel,
            folders_first=True,
            max_folders=1,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_FLAT,
        )

    assert all(item["type"] != "comment" for item in flat)
    folder_names = [item["name"] for item in flat if item["type"] == "folder"]
    assert folder_names == ["pkg", "dir_a", "dir_b"]


def test_file_tree_performance_guard_large_directory() -> None:
    base_rel = "tmp/tests/file_tree/performance_guard"
    with _project_directory(base_rel):
        structure = {f"dir{i}": {} for i in range(50)}
        files = {f"file{i}.txt": "" for i in range(4900)}
        structure.update(files)
        _materialize_structure(base_rel, structure)

        start = time.perf_counter()
        file_tree(
            base_rel,
            max_lines=200,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_STRING,
        )
        duration = time.perf_counter() - start

    assert duration < 2.0
