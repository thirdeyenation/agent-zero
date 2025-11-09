from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
import time

import pytest

from python.helpers.files import (
    OUTPUT_MODE_FLAT,
    OUTPUT_MODE_STRING,
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


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "file_tree"


def _load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8").rstrip("\n")


@contextmanager
def _project_directory(relative_path: str):
    delete_dir(relative_path)
    try:
        create_dir(relative_path)
        yield Path(get_abs_path(relative_path))
    finally:
        delete_dir(relative_path)


def _materialize_structure(base_rel: str, structure: dict[str, object]) -> None:
    for entry, value in structure.items():
        rel = os.path.join(base_rel, entry)
        if isinstance(value, dict):
            create_dir(rel)
            _materialize_structure(rel, value)
        else:
            content = "" if value is None else str(value)
            write_file(rel, content)


def _set_entry_times(relative_path: str, timestamp: float) -> None:
    abs_path = get_abs_path(relative_path)
    os.utime(abs_path, (timestamp, timestamp))
    time.sleep(0.01)


def _extract_tree_labels(result: str) -> list[str]:
    labels: list[str] = []
    for line in result.splitlines()[1:]:
        if "── " in line:
            labels.append(line.split("── ", 1)[1])
    return labels


def test_file_tree_string_breadth_first_snapshot() -> None:
    base_rel = "tmp/tests/file_tree/string_breadth_first"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "alpha": {
                    "alpha_file.txt": "alpha",
                    "nested": {"inner.txt": "inner"},
                },
                "beta": {
                    "beta_file.txt": "beta",
                },
                "zeta": {},
                "a.txt": "A",
                "b.txt": "B",
            },
        )

        result = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_STRING,
        )

    assert result == _load_fixture("string_breadth_first.txt")


def test_file_tree_string_ignore_and_limits() -> None:
    base_rel = "tmp/tests/file_tree/string_ignore_limits"
    ignore_file_rel = os.path.join(base_rel, ".treeignore")
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "src": {
                    "main.py": "print('hello')",
                    "utils.py": "pass",
                    "tmp.tmp": "",
                    "cache": {
                        "cached.txt": "",
                        "keep.txt": "",
                    },
                    "modules": {
                        "a.py": "",
                        "b.py": "",
                        "c.py": "",
                    },
                },
                "logs": {
                    "2024.log": "",
                    "2025.log": "",
                },
                "notes.md": "",
                "build.tmp": "",
            },
        )

        write_file(
            ignore_file_rel,
            "\n".join(
                [
                    "*.tmp",
                    "cache/",
                    "!src/cache/keep.txt",
                    "logs/",
                    "!logs/2025.log",
                ]
            ),
        )

        result = file_tree(
            base_rel,
            folders_first=False,
            sort=(SORT_BY_NAME, SORT_ASC),
            ignore="file:.treeignore",
            max_folders=1,
            max_files=2,
            max_lines=12,
            output_mode=OUTPUT_MODE_STRING,
        )

    assert result == _load_fixture("string_ignore_limits.txt")


def test_file_tree_string_single_overflow_promotes_entry() -> None:
    base_rel = "tmp/tests/file_tree/string_single_overflow"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "first_dir": {},
                "second_dir": {},
            },
        )

        result = file_tree(
            base_rel,
            folders_first=True,
            max_folders=1,
            sort=(SORT_BY_NAME, SORT_DESC),
            output_mode=OUTPUT_MODE_STRING,
        )

    assert "# 1 more folder" not in result
    lines = result.splitlines()
    assert any(line.endswith("first_dir/") for line in lines)
    assert any(line.endswith("second_dir/") for line in lines)


def test_file_tree_string_summary_comment_after_children() -> None:
    base_rel = "tmp/tests/file_tree/string_comment_order"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "logs": {
                    "2025.log": "",
                },
                "alpha": {},
                "beta": {},
                "gamma": {},
            },
        )

        result = file_tree(
            base_rel,
            folders_first=True,
            max_folders=1,
            sort=(SORT_BY_NAME, SORT_DESC),
            output_mode=OUTPUT_MODE_STRING,
        )

    lines = result.splitlines()
    comment_index = next(i for i, line in enumerate(lines) if "# 3 more folders" in line)
    logs_index = next(i for i, line in enumerate(lines) if line.endswith("logs/"))
    child_index = next(i for i, line in enumerate(lines) if line.strip().endswith("2025.log"))
    assert logs_index < child_index < comment_index


def test_file_tree_string_sort_all_keys() -> None:
    base_rel = "tmp/tests/file_tree/string_sort_all_keys"
    with _project_directory(base_rel) as base_abs:
        _materialize_structure(
            base_rel,
            {
                "folder_alpha": {},
                "folder_beta": {},
                "file_first.txt": "",
                "file_second.txt": "",
                "file_third.txt": "",
            },
        )
        base_timestamp = time.time()
        for offset, name in enumerate(
            [
                "folder_alpha",
                "folder_beta",
                "file_first.txt",
                "file_second.txt",
                "file_third.txt",
            ],
            start=1,
        ):
            _set_entry_times(os.path.join(base_rel, name), base_timestamp + offset)

        stats: dict[str, dict[str, object]] = {}
        for name in sorted(os.listdir(base_abs)):
            abs_entry = base_abs / name
            stat = os.stat(abs_entry, follow_symlinks=False)
            stats[name] = {
                "is_dir": abs_entry.is_dir(),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
            }

        sort_variants = [
            (SORT_BY_NAME, SORT_ASC),
            (SORT_BY_NAME, SORT_DESC),
            (SORT_BY_CREATED, SORT_ASC),
            (SORT_BY_CREATED, SORT_DESC),
            (SORT_BY_MODIFIED, SORT_ASC),
            (SORT_BY_MODIFIED, SORT_DESC),
        ]

        results = {
            variant: file_tree(
                base_rel,
                folders_first=True,
                sort=variant,
                output_mode=OUTPUT_MODE_STRING,
            )
            for variant in sort_variants
        }

    def expected_labels(key: str, direction: str) -> list[str]:
        reverse = direction == SORT_DESC
        folders = [(name, stats[name]) for name in stats if stats[name]["is_dir"]]
        files = [(name, stats[name]) for name in stats if not stats[name]["is_dir"]]

        def sort_key(item):
            name, meta = item
            if key == SORT_BY_NAME:
                return name.casefold()
            if key == SORT_BY_CREATED:
                return meta["created"]
            return meta["modified"]

        folders_sorted = sorted(folders, key=sort_key, reverse=reverse)
        files_sorted = sorted(files, key=sort_key, reverse=reverse)
        labels = [f"{name}/" for name, _ in folders_sorted]
        labels.extend(name for name, _ in files_sorted)
        return labels

    for key, direction in sort_variants:
        labels = _extract_tree_labels(results[(key, direction)])
        assert labels == expected_labels(key, direction)


def test_file_tree_string_missing_path() -> None:
    with pytest.raises(FileNotFoundError):
        file_tree(
            "tmp/tests/file_tree/does_not_exist",
            output_mode=OUTPUT_MODE_STRING,
        )


def test_file_tree_string_empty_directory() -> None:
    base_rel = "tmp/tests/file_tree/string_empty"
    with _project_directory(base_rel):
        result = file_tree(base_rel, output_mode=OUTPUT_MODE_STRING)
    assert result == "tmp/tests/file_tree/string_empty/"


def test_file_tree_string_folders_first_disabled() -> None:
    base_rel = "tmp/tests/file_tree/string_folders_first"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "folder": {"child.txt": ""},
                "alpha.txt": "",
            },
        )
        result = file_tree(
            base_rel,
            folders_first=False,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_STRING,
        )
    lines = result.splitlines()
    assert lines[1] == "├── alpha.txt"  # file precedes folder when folders_first=False


def test_file_tree_string_max_depth_levels() -> None:
    base_rel = "tmp/tests/file_tree/string_max_depth"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "level1": {
                    "level2": {
                        "level3.txt": "",
                    },
                },
            },
        )
        depth_one = file_tree(
            base_rel,
            max_depth=1,
            output_mode=OUTPUT_MODE_STRING,
        )
        depth_two = file_tree(
            base_rel,
            max_depth=2,
            output_mode=OUTPUT_MODE_STRING,
        )
    assert depth_one.splitlines() == ["tmp/tests/file_tree/string_max_depth/", "└── level1/"]
    assert "level2/" in depth_two


def test_file_tree_string_bfs_regression_flat_levels() -> None:
    base_rel = "tmp/tests/file_tree/string_bfs_regression"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dirA": {"a1.txt": "", "a2.txt": ""},
                "dirB": {"b1.txt": ""},
                "root.txt": "",
            },
        )
        flat = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            output_mode=OUTPUT_MODE_FLAT,
        )
    levels = [item["level"] for item in flat]
    assert levels[0] == 1
    for current, nxt in zip(levels, levels[1:]):
        assert nxt <= current + 1, "level jumps exceed single depth step"


def test_file_tree_string_deep_structure_limits() -> None:
    base_rel = "tmp/tests/file_tree/string_deep_limits"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "layer1_a": {
                    "layer2_a": {
                        "layer3_a": {
                            "layer4_a": {
                                "layer5_a.txt": "",
                            }
                        }
                    }
                },
                "layer1_b": {
                    "layer2_b": {
                        "layer3_b": {
                            "layer4_b": {
                                "layer5_b.txt": "",
                            }
                        }
                    }
                },
                "root_file.txt": "",
            },
        )

        result = file_tree(
            base_rel,
            max_lines=6,
            output_mode=OUTPUT_MODE_STRING,
        )

    lines = result.splitlines()
    deep_names = {"layer4_a/", "layer5_a.txt", "layer4_b/", "layer5_b.txt"}
    combined = "\n".join(lines)
    for name in deep_names:
        assert name not in combined
    assert lines[1:] == [
        "├── layer1_b/",
        "│   └── layer2_b/",
        "│       └── layer3_b/",
        "├── layer1_a/",
        "│   └── layer2_a/",
        "│       └── layer3_a/",
        "└── root_file.txt",
    ]


def test_file_tree_string_files_first_max_lines_modified() -> None:
    base_rel = "tmp/tests/file_tree/string_files_first_modified"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "dir": {
                    "inner_a.txt": "",
                    "inner_b.txt": "",
                },
                "alpha.txt": "",
                "beta.txt": "",
                "gamma.txt": "",
            },
        )
        base_ts = time.time()
        for offset, rel_path in enumerate(
            [
                "dir",
                os.path.join("dir", "inner_a.txt"),
                os.path.join("dir", "inner_b.txt"),
                "alpha.txt",
                "beta.txt",
                "gamma.txt",
            ],
            start=1,
        ):
            _set_entry_times(os.path.join(base_rel, rel_path), base_ts + offset)

        result = file_tree(
            base_rel,
            folders_first=False,
            sort=(SORT_BY_MODIFIED, SORT_DESC),
            max_lines=4,
            output_mode=OUTPUT_MODE_STRING,
        )

    lines = result.splitlines()
    assert len(lines) == 5  # root + 4 entries
    assert lines[1].endswith("gamma.txt")
    assert "inner_b.txt" not in result


def test_file_tree_string_zero_file_limit_unlimited() -> None:
    base_rel = "tmp/tests/file_tree/string_zero_limit"
    with _project_directory(base_rel):
        _materialize_structure(
            base_rel,
            {
                "folder1": {},
                "folder2": {},
                "folder3": {},
                "a.py": "",
                "b.py": "",
                "c.py": "",
            },
        )

        result = file_tree(
            base_rel,
            folders_first=True,
            sort=(SORT_BY_NAME, SORT_ASC),
            max_folders=1,
            max_files=0,
            output_mode=OUTPUT_MODE_STRING,
        )

    lines = result.splitlines()
    assert any("# 2 more folders" in line for line in lines)
    assert all("more files" not in line for line in lines)
    assert "a.py" in result and "c.py" in result
