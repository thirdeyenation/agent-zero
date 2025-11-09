from __future__ import annotations

import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import pytest

from python.helpers.files import (
    OUTPUT_MODE_FLAT,
    OUTPUT_MODE_NESTED,
    SORT_ASC,
    SORT_BY_CREATED,
    SORT_BY_MODIFIED,
    SORT_BY_NAME,
    SORT_DESC,
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


def _set_entry_times(relative_path: str, timestamp: float) -> None:
    abs_path = get_abs_path(relative_path)
    os.utime(abs_path, (timestamp, timestamp))
    time.sleep(0.01)


def _collect_expected_stats(base_abs: Path) -> dict[str, tuple[datetime, datetime]]:
    results: dict[str, tuple[datetime, datetime]] = {}
    for current_path, dirnames, filenames in os.walk(base_abs):
        for name in dirnames + filenames:
            path = os.path.join(current_path, name)
            stat = os.stat(path, follow_symlinks=False)
            created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
            modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            results[name] = (created, modified)
    return results


def _flatten_nested(items: list[dict]) -> list[dict]:
    result: list[dict] = []
    for item in items:
        result.append(item)
        if item.get("items"):
            result.extend(_flatten_nested(item["items"]))
    return result


def _assert_datetime_order(values: list[datetime], direction: str) -> None:
    expected = sorted(values, reverse=direction == SORT_DESC)
    assert values == expected


def test_file_tree_flat_metadata_and_levels() -> None:
    base_rel = "tmp/tests/file_tree/flat_metadata"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dirA": {
                    "file1.txt": "",
                    "file2.txt": "",
                },
                "dirB": {
                    "sub": {
                        "inner.txt": "",
                    },
                },
                "root.txt": "",
            },
        )

        flat = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_FLAT,
        )
        flat_files_first = file_tree(
            base_rel,
            folders_first=False,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_FLAT,
        )

    assert all("items" in item for item in flat)
    assert all(item["type"] in {"file", "folder", "comment"} for item in flat)

    # Ensure datetime fields are timezone-aware UTC
    for item in flat:
        assert item["created"].tzinfo is not None
        assert item["modified"].tzinfo is not None

    # Level ordering: first three entries should be level 1 (dirA, dirB, root.txt)
    levels = [item["level"] for item in flat]
    level_one_names = [item["name"] for item in flat if item["level"] == 1]
    assert level_one_names == ["dirA", "dirB", "root.txt"]
    assert flat[0]["type"] == "folder"
    assert flat_files_first[0]["type"] == "file"


def test_file_tree_flat_sort_all_keys() -> None:
    base_rel = "tmp/tests/file_tree/flat_sort_all_keys"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dir_first": {},
                "dir_second": {},
                "file_alpha.txt": "",
                "file_beta.txt": "",
                "file_gamma.txt": "",
            },
        )
        base_timestamp = time.time()
        for offset, name in enumerate(
            ["dir_first", "dir_second", "file_alpha.txt", "file_beta.txt", "file_gamma.txt"],
            start=1,
        ):
            _set_entry_times(os.path.join(base_rel, name), base_timestamp + offset)

        flat_results = {
            (key, direction): file_tree(
                base_rel,
                folders_first=False,
                sort=(key, direction),
                output_mode=OUTPUT_MODE_FLAT,
            )
            for key in (SORT_BY_NAME, SORT_BY_CREATED, SORT_BY_MODIFIED)
            for direction in (SORT_ASC, SORT_DESC)
        }

    for (key, direction), items in flat_results.items():
        filtered = [item for item in items if item["type"] != "comment"]
        folders = [item for item in filtered if item["type"] == "folder"]
        files = [item for item in filtered if item["type"] == "file"]

        if key == SORT_BY_NAME:
            file_names = [item["name"] for item in files]
            folder_names = [item["name"] for item in folders]
            assert file_names == sorted(file_names, reverse=direction == SORT_DESC)
            assert folder_names == sorted(folder_names, reverse=direction == SORT_DESC)
        elif key == SORT_BY_CREATED:
            file_created = [item["created"] for item in files]
            folder_created = [item["created"] for item in folders]
            _assert_datetime_order(file_created, direction)
            _assert_datetime_order(folder_created, direction)
        else:
            file_modified = [item["modified"] for item in files]
            folder_modified = [item["modified"] for item in folders]
            _assert_datetime_order(file_modified, direction)
            _assert_datetime_order(folder_modified, direction)


def test_file_tree_nested_structure_and_ignore() -> None:
    base_rel = "tmp/tests/file_tree/nested_structure"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "src": {
                    "a.py": "",
                    "b.py": "",
                    "cache": {
                        "ignored.py": "",
                        "keep.py": "",
                    },
                },
                "README.md": "",
            },
        )

        nested = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            ignore="cache/\n!src/cache/keep.py",
            output_mode=OUTPUT_MODE_NESTED,
        )

    assert isinstance(nested, list)
    src_node = next(node for node in nested if node["name"] == "src")
    src_children = {child["name"] for child in src_node["items"]}
    assert "cache" in src_children  # cache appears to host keep.py

    cache_node = next(child for child in src_node["items"] if child["name"] == "cache")
    cache_children = {child["name"] for child in cache_node["items"]}
    assert "keep.py" in cache_children
    assert "ignored.py" not in cache_children
    assert [child["name"] for child in src_node["items"]] == ["cache", "a.py", "b.py"]


def test_file_tree_nested_sort_all_keys() -> None:
    base_rel = "tmp/tests/file_tree/nested_sort_all_keys"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dir_first": {
                    "inner_a.txt": "",
                    "inner_b.txt": "",
                },
                "dir_second": {
                    "nested_dir": {
                        "deep_file.txt": "",
                    },
                },
                "file_alpha.txt": "",
            },
        )
        base_timestamp = time.time()
        for offset, rel_path in enumerate(
            [
                "dir_first",
                os.path.join("dir_first", "inner_a.txt"),
                os.path.join("dir_first", "inner_b.txt"),
                "dir_second",
                os.path.join("dir_second", "nested_dir"),
                os.path.join("dir_second", "nested_dir", "deep_file.txt"),
                "file_alpha.txt",
            ],
            start=1,
        ):
            _set_entry_times(os.path.join(base_rel, rel_path), base_timestamp + offset)

        nested_results = {
            (key, direction): file_tree(
                base_rel,
                folders_first=False,
                sort=(key, direction),
                output_mode=OUTPUT_MODE_NESTED,
            )
            for key in (SORT_BY_NAME, SORT_BY_CREATED, SORT_BY_MODIFIED)
            for direction in (SORT_ASC, SORT_DESC)
        }

    def assert_nested_sorted(items: list[dict], key: str, direction: str) -> None:
        filtered = [item for item in items if item["type"] != "comment"]
        if not filtered:
            return
        folders = [item for item in filtered if item["type"] == "folder"]
        files = [item for item in filtered if item["type"] == "file"]

        def assert_group(group: list[dict], attr: str) -> None:
            values = [entry[attr] for entry in group]
            if attr == "name":
                assert values == sorted(values, reverse=direction == SORT_DESC)
            else:
                _assert_datetime_order(values, direction)

        if key == SORT_BY_NAME:
            assert_group(files, "name")
            assert_group(folders, "name")
        elif key == SORT_BY_CREATED:
            assert_group(files, "created")
            assert_group(folders, "created")
        else:
            assert_group(files, "modified")
            assert_group(folders, "modified")

        for child in folders + files:
            if child.get("items"):
                assert_nested_sorted(child["items"], key, direction)

    for (key, direction), items in nested_results.items():
        assert_nested_sorted(items, key, direction)


def test_file_tree_nested_respects_max_depth() -> None:
    base_rel = "tmp/tests/file_tree/nested_max_depth"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "top": {
                    "branch": {
                        "leaf.txt": "",
                    },
                },
            },
        )

        nested = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            max_depth=1,
            output_mode=OUTPUT_MODE_NESTED,
        )

    top_node = nested[0]
    assert top_node["items"] == []  # depth limited, children omitted


def test_file_tree_flat_and_nested_timestamps_match_filesystem() -> None:
    base_rel = "tmp/tests/file_tree/timestamp_accuracy"
    with _project_directory(base_rel) as base_abs:
        _materialize_structure(
            base_rel,
            {
                "folder_root": {
                    "folder_branch": {
                        "leaf_unique.txt": "",
                    },
                    "leaf_second.txt": "",
                },
                "file_standalone.txt": "",
            },
        )

        expected_stats = _collect_expected_stats(base_abs)
        flat = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_FLAT,
        )
        nested = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_NESTED,
        )

    def assert_matches(item: dict) -> None:
        if item["type"] == "comment":
            return
        created, modified = expected_stats[item["name"]]
        assert item["created"] == created
        assert item["modified"] == modified

    for entry in flat:
        assert_matches(entry)

    for entry in _flatten_nested(nested):
        assert_matches(entry)


def test_file_tree_nested_summary_comments() -> None:
    base_rel = "tmp/tests/file_tree/nested_summary_comments"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "folder_root": {
                    "keep_me.txt": "",
                    "omit_me.txt": "",
                    "omit_me_too.txt": "",
                }
            },
        )
        base_timestamp = time.time()
        _set_entry_times(os.path.join(base_rel, "folder_root/keep_me.txt"), base_timestamp + 3)
        _set_entry_times(os.path.join(base_rel, "folder_root/omit_me.txt"), base_timestamp + 1)
        _set_entry_times(os.path.join(base_rel, "folder_root/omit_me_too.txt"), base_timestamp + 2)

        nested = file_tree(
            base_rel,
            folders_first=True,
            max_files=1,
            output_mode=OUTPUT_MODE_NESTED,
        )

    folder_node = nested[0]
    assert folder_node["name"] == "folder_root"
    child_items = folder_node["items"]
    assert child_items is not None
    comment_nodes = [item for item in child_items if item["type"] == "comment"]
    assert comment_nodes, "Expected summary comment for truncated children"
    comment_label = comment_nodes[0]["text"].split("── ", 1)[-1]
    assert comment_label.startswith("# ")
    file_names = [item["name"] for item in child_items if item["type"] == "file"]
    assert file_names == ["keep_me.txt"]
    assert comment_nodes[0] is child_items[-1]
    assert comment_nodes[0]["items"] is None


def test_file_tree_flat_files_first_limits() -> None:
    base_rel = "tmp/tests/file_tree/flat_files_first_limits"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dir1": {},
                "dir2": {},
                "dir3": {},
                "dir4": {},
                "a.txt": "",
                "b.txt": "",
                "c.txt": "",
            },
        )

        flat = file_tree(
            base_rel,
            folders_first=False,
            max_folders=1,
            max_files=1,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_FLAT,
        )

    comment_nodes = [item for item in flat if item["type"] == "comment"]
    assert {node["name"] for node in comment_nodes} == {"3 more folders", "2 more files"}
    assert flat[0]["type"] == "file"  # files come first when folders_first=False


def test_file_tree_flat_sort_created_max_lines() -> None:
    base_rel = "tmp/tests/file_tree/flat_sort_created_max_lines"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dirA": {"inner.txt": ""},
                "file1.txt": "",
                "file2.txt": "",
                "file3.txt": "",
            },
        )
        base_ts = time.time()
        for offset, rel_path in enumerate(
            [
                "dirA",
                os.path.join("dirA", "inner.txt"),
                "file1.txt",
                "file2.txt",
                "file3.txt",
            ],
            start=1,
        ):
            _set_entry_times(os.path.join(base_rel, rel_path), base_ts + offset)

        flat = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_CREATED, SORT_DESC),
            max_lines=4,
            output_mode=OUTPUT_MODE_FLAT,
        )

    assert len(flat) == 4
    assert flat[0]["name"] == "dirA"
    file_names = [item["name"] for item in flat if item["type"] == "file"]
    assert file_names == ["file3.txt", "file2.txt", "file1.txt"]


def test_file_tree_nested_files_first_limits() -> None:
    base_rel = "tmp/tests/file_tree/nested_files_first_limits"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dir": {
                    "a.py": "",
                    "b.py": "",
                    "c.py": "",
                },
                "folder_a": {"inner.txt": ""},
                "folder_b": {},
                "folder_c": {},
            },
        )

        nested = file_tree(
            base_rel,
            folders_first=False,
            max_folders=1,
            max_files=1,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_NESTED,
        )

    root = nested
    comment_nodes = [item for item in root if item["type"] == "comment"]
    assert comment_nodes
    assert any("more folders" in node["text"] for node in comment_nodes)
    all_nodes = _flatten_nested(root)
    file_comment_nodes = [item for item in all_nodes if item["type"] == "comment" and "more files" in item["text"]]
    assert file_comment_nodes, "Expected file summary comment within nested structure"


def test_file_tree_nested_max_depth_with_sort() -> None:
    base_rel = "tmp/tests/file_tree/nested_max_depth_sort"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "root": {
                    "branch": {
                        "leaf_a.txt": "",
                        "leaf_b.txt": "",
                    },
                },
                "alpha.txt": "",
            },
        )
        base_ts = time.time()
        for offset, rel_path in enumerate(
            [
                "root",
                os.path.join("root", "branch"),
                os.path.join("root", "branch", "leaf_a.txt"),
                os.path.join("root", "branch", "leaf_b.txt"),
                "alpha.txt",
            ],
            start=1,
        ):
            _set_entry_times(os.path.join(base_rel, rel_path), base_ts + offset)

        nested = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_CREATED, SORT_ASC),
            max_depth=2,
            output_mode=OUTPUT_MODE_NESTED,
        )

    root_node = next(item for item in nested if item["name"] == "root")
    assert root_node["items"] is not None
    branch_node = next(child for child in root_node["items"] if child["name"] == "branch")
    assert branch_node["items"] == []


def test_file_tree_nested_global_max_lines_prunes_depth() -> None:
    base_rel = "tmp/tests/file_tree/nested_max_lines"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dirA": {
                    "a1.txt": "",
                    "a2.txt": "",
                },
                "dirB": {
                    "b1.txt": "",
                    "b2.txt": "",
                },
                "root_file.txt": "",
            },
        )

        nested = file_tree(
            base_rel,
            folders_first=True,
            max_lines=4,
            output_mode=OUTPUT_MODE_NESTED,
        )

    flattened = _flatten_nested(nested)
    levels = [item["level"] for item in flattened]
    assert all(level <= 2 for level in levels)
    top_level = [item for item in flattened if item["level"] == 1]
    assert {item["name"] for item in top_level} == {"dirA", "dirB", "root_file.txt"}
