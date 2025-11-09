from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from fnmatch import fnmatch
import json
import os
import re
import base64
import shutil
import tempfile
from typing import Any, Callable, Iterable, Literal, Optional, Sequence, Type, cast
import zipfile
import glob
import mimetypes

from pathspec import PathSpec


class VariablesPlugin(ABC):
    @abstractmethod
    def get_variables(
        self, file: str, backup_dirs: list[str] | None = None
    ) -> dict[str, Any]:  # type: ignore[override]
        pass


def load_plugin_variables(
    file: str, backup_dirs: list[str] | None = None
) -> dict[str, Any]:
    if not file.endswith(".md"):
        return {}

    if backup_dirs is None:
        backup_dirs = []

    try:
        # Create filename and directories list
        plugin_filename = basename(file, ".md") + ".py"
        directories = [dirname(file)] + backup_dirs
        plugin_file = find_file_in_dirs(plugin_filename, directories)
    except FileNotFoundError:
        plugin_file = None

    if plugin_file and exists(plugin_file):

        from python.helpers import extract_tools

        plugin_base: Any = VariablesPlugin
        classes = extract_tools.load_classes_from_file(
            plugin_file, plugin_base, one_per_file=False
        )
        for cls in classes:
            if isinstance(cls, type) and issubclass(cls, VariablesPlugin):
                plugin_cls = cast(Type[VariablesPlugin], cls)
                return plugin_cls().get_variables(file, backup_dirs)

        # load python code and extract variables variables from it
        # module = None
        # module_name = dirname(plugin_file).replace("/", ".") + "." + basename(plugin_file, '.py')

        # try:
        #     spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        #     if not spec:
        #         return {}
        #     module = importlib.util.module_from_spec(spec)
        #     sys.modules[spec.name] = module
        #     spec.loader.exec_module(module)  # type: ignore
        # except ImportError:
        #     return {}

        # if module is None:
        #     return {}

        # # Get all classes in the module
        # class_list = inspect.getmembers(module, inspect.isclass)
        # # Filter for classes that are subclasses of VariablesPlugin
        # # iterate backwards to skip imported superclasses
        # for cls in reversed(class_list):
        #     if cls[1] is not VariablesPlugin and issubclass(cls[1], VariablesPlugin):
        #         return cls[1]().get_variables()  # type: ignore
    return {}


from python.helpers.strings import sanitize_string


def parse_file(
    _filename: str, _directories: list[str] | None = None, _encoding="utf-8", **kwargs
):
    if _directories is None:
        _directories = []

    # Find the file in the directories
    absolute_path = find_file_in_dirs(_filename, _directories)

    # Read the file content
    with open(absolute_path, "r", encoding=_encoding) as f:
        # content = remove_code_fences(f.read())
        content = f.read()

    is_json = is_full_json_template(content)
    content = remove_code_fences(content)
    variables = load_plugin_variables(absolute_path, _directories) or {}  # type: ignore
    variables.update(kwargs)
    if is_json:
        content = replace_placeholders_json(content, **variables)
        obj = json.loads(content)
        # obj = replace_placeholders_dict(obj, **variables)
        return obj
    else:
        content = replace_placeholders_text(content, **variables)
        # Process include statements
        content = process_includes(
            # here we use kwargs, the plugin variables are not inherited
            content,
            _directories,
            **kwargs,
        )
        return content


def read_prompt_file(
    _file: str, _directories: list[str] | None = None, _encoding="utf-8", **kwargs
):
    if _directories is None:
        _directories = []

    # If filename contains folder path, extract it and add to directories
    if os.path.dirname(_file):
        folder_path = os.path.dirname(_file)
        _file = os.path.basename(_file)
        _directories = [folder_path] + _directories

    # Find the file in the directories
    absolute_path = find_file_in_dirs(_file, _directories)

    # Read the file content
    with open(absolute_path, "r", encoding=_encoding) as f:
        # content = remove_code_fences(f.read())
        content = f.read()

    variables = load_plugin_variables(_file, _directories) or {}  # type: ignore
    variables.update(kwargs)

    # Replace placeholders with values from kwargs
    content = replace_placeholders_text(content, **variables)

    # Process include statements
    content = process_includes(
        # here we use kwargs, the plugin variables are not inherited
        content,
        _directories,
        **kwargs,
    )

    return content


def read_file(relative_path: str, encoding="utf-8"):
    # Try to get the absolute path for the file from the original directory or backup directories
    absolute_path = get_abs_path(relative_path)

    # Read the file content
    with open(absolute_path, "r", encoding=encoding) as f:
        return f.read()


def read_file_bin(relative_path: str):
    # Try to get the absolute path for the file from the original directory or backup directories
    absolute_path = get_abs_path(relative_path)

    # read binary content
    with open(absolute_path, "rb") as f:
        return f.read()


def read_file_base64(relative_path):
    # get absolute path
    absolute_path = get_abs_path(relative_path)

    # read binary content and encode to base64
    with open(absolute_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def replace_placeholders_text(_content: str, **kwargs):
    # Replace placeholders with values from kwargs
    for key, value in kwargs.items():
        placeholder = "{{" + key + "}}"
        strval = str(value)
        _content = _content.replace(placeholder, strval)
    return _content


def replace_placeholders_json(_content: str, **kwargs):
    # Replace placeholders with values from kwargs
    for key, value in kwargs.items():
        placeholder = "{{" + key + "}}"
        strval = json.dumps(value)
        _content = _content.replace(placeholder, strval)
    return _content


def replace_placeholders_dict(_content: dict, **kwargs):
    def replace_value(value):
        if isinstance(value, str):
            placeholders = re.findall(r"{{(\w+)}}", value)
            if placeholders:
                for placeholder in placeholders:
                    if placeholder in kwargs:
                        replacement = kwargs[placeholder]
                        if value == f"{{{{{placeholder}}}}}":
                            return replacement
                        elif isinstance(replacement, (dict, list)):
                            value = value.replace(
                                f"{{{{{placeholder}}}}}", json.dumps(replacement)
                            )
                        else:
                            value = value.replace(
                                f"{{{{{placeholder}}}}}", str(replacement)
                            )
            return value
        elif isinstance(value, dict):
            return {k: replace_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [replace_value(item) for item in value]
        else:
            return value

    return replace_value(_content)


def process_includes(_content: str, _directories: list[str], **kwargs):
    # Regex to find {{ include 'path' }} or {{include'path'}}
    include_pattern = re.compile(r"{{\s*include\s*['\"](.*?)['\"]\s*}}")

    def replace_include(match):
        include_path = match.group(1)
        # if the path is absolute, do not process it
        if os.path.isabs(include_path):
            return match.group(0)
        # Search for the include file in the directories
        try:
            included_content = read_prompt_file(include_path, _directories, **kwargs)
            return included_content
        except FileNotFoundError:
            return match.group(0)  # Return original if file not found

    # Replace all includes with the file content
    return re.sub(include_pattern, replace_include, _content)


def find_file_in_dirs(_filename: str, _directories: list[str]):
    """
    This function searches for a filename in a list of directories in order.
    Returns the absolute path of the first found file.
    """
    # Loop through the directories in order
    for directory in _directories:
        # Create full path
        full_path = get_abs_path(directory, _filename)
        if exists(full_path):
            return full_path

    # If the file is not found, raise FileNotFoundError
    raise FileNotFoundError(
        f"File '{_filename}' not found in any of the provided directories."
    )


def get_unique_filenames_in_dirs(dir_paths: list[str], pattern: str = "*"):
    # returns absolute paths for unique filenames, priority by order in dir_paths
    seen = set()
    result = []
    for dir_path in dir_paths:
        full_dir = get_abs_path(dir_path)
        for file_path in glob.glob(os.path.join(full_dir, pattern)):
            fname = os.path.basename(file_path)
            if fname not in seen and os.path.isfile(file_path):
                seen.add(fname)
                result.append(get_abs_path(file_path))
    # sort by filename (basename), not the full path
    result.sort(key=lambda path: os.path.basename(path))
    return result


def remove_code_fences(text):
    # Pattern to match code fences with optional language specifier
    pattern = r"(```|~~~)(.*?\n)(.*?)(\1)"

    # Function to replace the code fences
    def replacer(match):
        return match.group(3)  # Return the code without fences

    # Use re.DOTALL to make '.' match newlines
    result = re.sub(pattern, replacer, text, flags=re.DOTALL)

    return result


def is_full_json_template(text):
    # Pattern to match the entire text enclosed in ```json or ~~~json fences
    pattern = r"^\s*(```|~~~)\s*json\s*\n(.*?)\n\1\s*$"
    # Use re.DOTALL to make '.' match newlines
    match = re.fullmatch(pattern, text.strip(), flags=re.DOTALL)
    return bool(match)


def write_file(relative_path: str, content: str, encoding: str = "utf-8"):
    abs_path = get_abs_path(relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    content = sanitize_string(content, encoding)
    with open(abs_path, "w", encoding=encoding) as f:
        f.write(content)


def write_file_bin(relative_path: str, content: bytes):
    abs_path = get_abs_path(relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(content)


def write_file_base64(relative_path: str, content: str):
    # decode base64 string to bytes
    data = base64.b64decode(content)
    abs_path = get_abs_path(relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(data)


def delete_dir(relative_path: str):
    # ensure deletion of directory without propagating errors
    abs_path = get_abs_path(relative_path)
    if os.path.exists(abs_path):
        # first try with ignore_errors=True which is the safest option
        shutil.rmtree(abs_path, ignore_errors=True)

        # if directory still exists, try more aggressive methods
        if os.path.exists(abs_path):
            try:
                # try to change permissions and delete again
                for root, dirs, files in os.walk(abs_path, topdown=False):
                    for name in files:
                        file_path = os.path.join(root, name)
                        os.chmod(file_path, 0o777)
                    for name in dirs:
                        dir_path = os.path.join(root, name)
                        os.chmod(dir_path, 0o777)

                # try again after changing permissions
                shutil.rmtree(abs_path, ignore_errors=True)
            except Exception:
                # suppress all errors - we're ensuring no errors propagate
                pass


def move_dir(old_path: str, new_path: str):
    # rename/move the directory from old_path to new_path (both relative)
    abs_old = get_abs_path(old_path)
    abs_new = get_abs_path(new_path)
    if not os.path.isdir(abs_old):
        return  # nothing to rename
    try:
        os.rename(abs_old, abs_new)
    except Exception:
        pass  # suppress all errors, keep behavior consistent


# move dir safely, remove with number if needed
def move_dir_safe(src, dst, rename_format="{name}_{number}"):
    base_dst = dst
    i = 2
    while exists(dst):
        dst = rename_format.format(name=base_dst, number=i)
        i += 1
    move_dir(src, dst)
    return dst


# create dir safely, add number if needed
def create_dir_safe(dst, rename_format="{name}_{number}"):
    base_dst = dst
    i = 2
    while exists(dst):
        dst = rename_format.format(name=base_dst, number=i)
        i += 1
    create_dir(dst)
    return dst


def create_dir(relative_path: str):
    abs_path = get_abs_path(relative_path)
    os.makedirs(abs_path, exist_ok=True)


def list_files(relative_path: str, filter: str = "*"):
    abs_path = get_abs_path(relative_path)
    if not os.path.exists(abs_path):
        return []
    return [file for file in os.listdir(abs_path) if fnmatch(file, filter)]


def make_dirs(relative_path: str):
    abs_path = get_abs_path(relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)


def get_abs_path(*relative_paths):
    "Convert relative paths to absolute paths based on the base directory."
    return os.path.join(get_base_dir(), *relative_paths)


def deabsolute_path(path: str):
    "Convert absolute paths to relative paths based on the base directory."
    return os.path.relpath(path, get_base_dir())


def fix_dev_path(path: str):
    "On dev environment, convert /a0/... paths to local absolute paths"
    from python.helpers.runtime import is_development

    if is_development():
        if path.startswith("/a0/"):
            path = path.replace("/a0/", "")
    return get_abs_path(path)


def normalize_a0_path(path: str):
    "Convert absolute paths into /a0/... paths"
    if is_in_base_dir(path):
        deabs = deabsolute_path(path)
        return "/a0/" + deabs
    return path


def exists(*relative_paths):
    path = get_abs_path(*relative_paths)
    return os.path.exists(path)


def get_base_dir():
    # Get the base directory from the current file path
    base_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, "../../")))
    return base_dir


def basename(path: str, suffix: str | None = None):
    if suffix:
        return os.path.basename(path).removesuffix(suffix)
    return os.path.basename(path)


def dirname(path: str):
    return os.path.dirname(path)


def is_in_base_dir(path: str):
    # check if the given path is within the base directory
    base_dir = get_base_dir()
    # normalize paths to handle relative paths and symlinks
    abs_path = os.path.abspath(path)
    # check if the absolute path starts with the base directory
    return os.path.commonpath([abs_path, base_dir]) == base_dir


def get_subdirectories(
    relative_path: str,
    include: str | list[str] = "*",
    exclude: str | list[str] | None = None,
):
    abs_path = get_abs_path(relative_path)
    if not os.path.exists(abs_path):
        return []
    if isinstance(include, str):
        include = [include]
    if isinstance(exclude, str):
        exclude = [exclude]
    return [
        subdir
        for subdir in os.listdir(abs_path)
        if os.path.isdir(os.path.join(abs_path, subdir))
        and any(fnmatch(subdir, inc) for inc in include)
        and (exclude is None or not any(fnmatch(subdir, exc) for exc in exclude))
    ]


def zip_dir(dir_path: str):
    full_path = get_abs_path(dir_path)
    zip_file_path = tempfile.NamedTemporaryFile(suffix=".zip", delete=False).name
    base_name = os.path.basename(full_path)
    with zipfile.ZipFile(zip_file_path, "w", compression=zipfile.ZIP_DEFLATED) as zip:
        for root, _, files in os.walk(full_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, full_path)
                zip.write(file_path, os.path.join(base_name, rel_path))
    return zip_file_path


def move_file(relative_path: str, new_path: str):
    abs_path = get_abs_path(relative_path)
    new_abs_path = get_abs_path(new_path)
    os.makedirs(os.path.dirname(new_abs_path), exist_ok=True)
    os.rename(abs_path, new_abs_path)


def safe_file_name(filename: str) -> str:
    # Replace any character that's not alphanumeric, dash, underscore, or dot with underscore
    return re.sub(r"[^a-zA-Z0-9-._]", "_", filename)


def read_text_files_in_dir(
    dir_path: str, max_size: int = 1024 * 1024
) -> dict[str, str]:

    abs_path = get_abs_path(dir_path)
    if not os.path.exists(abs_path):
        return {}
    result = {}
    for file_path in [os.path.join(abs_path, f) for f in os.listdir(abs_path)]:
        try:
            if not os.path.isfile(file_path):
                continue
            if os.path.getsize(file_path) > max_size:
                continue
            mime, _ = mimetypes.guess_type(file_path)
            if mime is not None and not mime.startswith("text"):
                continue
            # Check if file is binary by reading a small chunk
            content = read_file(file_path)
            result[os.path.basename(file_path)] = content
        except Exception:
            continue
    return result


SORT_BY_NAME = "name"
SORT_BY_CREATED = "created"
SORT_BY_MODIFIED = "modified"

SORT_ASC = "asc"
SORT_DESC = "desc"

OUTPUT_MODE_STRING = "string"
OUTPUT_MODE_FLAT = "flat"
OUTPUT_MODE_NESTED = "nested"


def file_tree(
    relative_path: str,
    *,
    max_depth: int = 0,
    max_lines: int = 0,
    folders_first: bool = True,
    max_folders: int | None = None,
    max_files: int | None = None,
    sort: tuple[str, str] = (SORT_BY_MODIFIED, SORT_DESC),
    ignore: str | None = None,
    output_mode: str = OUTPUT_MODE_STRING,
) -> str | list[dict]:
    """Render a directory tree relative to the repository base path.

    Parameters:
        relative_path: Base directory (relative to project root) to scan with :func:`get_abs_path`.
        max_depth: Maximum depth of traversal (0 = unlimited). Depth starts at 1 for root entries.
        max_lines: Global limit for rendered lines (0 = unlimited). When exceeded, the current depth
            finishes rendering before deeper levels are skipped.
        folders_first: When True, folders render before files within each directory.
        max_folders: Optional per-directory cap (0 = unlimited) on rendered folder entries before adding a
            ``# N more folders`` comment. When only a single folder exceeds the limit and ``max_folders`` is greater than zero, that folder is rendered
            directly instead of emitting a summary comment.
        max_files: Optional per-directory cap (0 = unlimited) on rendered file entries before adding a ``# N more files`` comment.
            As with folders, a single excess file is rendered when ``max_files`` is greater than zero.
        sort: Tuple of ``(key, direction)`` where key is one of :data:`SORT_BY_NAME`,
            :data:`SORT_BY_CREATED`, or :data:`SORT_BY_MODIFIED`; direction is :data:`SORT_ASC`
            or :data:`SORT_DESC`.
        ignore: Inline ``.gitignore`` content or ``file:`` reference. Examples::

                ignore=\"\"\"\\n*.pyc\\n__pycache__/\\n!important.py\\n\"\"\"
                ignore=\"file:.gitignore\"         # relative to scan root
                ignore=\"file://.gitignore\"       # URI-style relative path
                ignore=\"file:/abs/path/.gitignore\"
                ignore=\"file:///abs/path/.gitignore\"

        output_mode: One of :data:`OUTPUT_MODE_STRING`, :data:`OUTPUT_MODE_FLAT`, or
            :data:`OUTPUT_MODE_NESTED`.

    Returns:
        ``OUTPUT_MODE_STRING`` → ``str``: multi-line ASCII tree.
        ``OUTPUT_MODE_FLAT`` → ``list[dict]``: flattened sequence of TreeItem dictionaries.
        ``OUTPUT_MODE_NESTED`` → ``list[dict]``: nested TreeItem dictionaries where folders
        include ``items`` arrays.

    Notes:
        * The utility is synchronous; avoid calling from latency-sensitive async loops.
        * The ASCII renderer walks the established tree depth-first so connectors reflect parent/child structure,
          while traversal and limit calculations remain breadth-first by depth.
        * ``created`` and ``modified`` values in structured outputs are timezone-aware UTC
          :class:`datetime.datetime` objects::

                item = flat_items[0]
                iso = item[\"created\"].isoformat()
                epoch = item[\"created\"].timestamp()

    """
    abs_root = get_abs_path(relative_path)

    if not os.path.exists(abs_root):
        raise FileNotFoundError(f"Path does not exist: {relative_path!r}")
    if not os.path.isdir(abs_root):
        raise NotADirectoryError(f"Expected a directory, received: {relative_path!r}")

    sort_key, sort_direction = sort
    if sort_key not in {SORT_BY_NAME, SORT_BY_CREATED, SORT_BY_MODIFIED}:
        raise ValueError(f"Unsupported sort key: {sort_key!r}")
    if sort_direction not in {SORT_ASC, SORT_DESC}:
        raise ValueError(f"Unsupported sort direction: {sort_direction!r}")
    if output_mode not in {OUTPUT_MODE_STRING, OUTPUT_MODE_FLAT, OUTPUT_MODE_NESTED}:
        raise ValueError(f"Unsupported output mode: {output_mode!r}")
    if max_depth < 0:
        raise ValueError("max_depth must be >= 0")
    if max_lines < 0:
        raise ValueError("max_lines must be >= 0")

    ignore_spec = _resolve_ignore_patterns(ignore, abs_root)

    root_stat = os.stat(abs_root, follow_symlinks=False)
    root_name = os.path.basename(os.path.normpath(abs_root)) or os.path.basename(abs_root)
    root_node = _TreeEntry(
        name=root_name,
        level=0,
        item_type="folder",
        created=datetime.fromtimestamp(root_stat.st_ctime, tz=timezone.utc),
        modified=datetime.fromtimestamp(root_stat.st_mtime, tz=timezone.utc),
        parent=None,
        items=[],
        rel_path="",
    )

    queue: deque[tuple[_TreeEntry, str, int]] = deque([(root_node, abs_root, 1)])
    nodes_in_order: list[_TreeEntry] = []
    limit_level: Optional[int] = None
    visibility_cache: dict[str, bool] = {}

    def make_entry(entry: os.DirEntry, parent: _TreeEntry, level: int, item_type: Literal["file", "folder"]) -> _TreeEntry:
        stat = entry.stat(follow_symlinks=False)
        rel_path = os.path.relpath(entry.path, abs_root)
        rel_posix = _normalize_relative_path(rel_path)
        return _TreeEntry(
            name=entry.name,
            level=level,
            item_type=item_type,
            created=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
            modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            parent=parent,
            items=[] if item_type == "folder" else None,
            rel_path=rel_posix,
        )

    while queue:
        parent_node, current_dir, level = queue.popleft()

        if max_depth and level > max_depth:
            continue

        remaining_depth = max_depth - level if max_depth else -1
        folders, files = _list_directory_children(
            current_dir,
            abs_root,
            ignore_spec,
            max_depth_remaining=remaining_depth,
            cache=visibility_cache,
        )

        folder_entries = [make_entry(folder, parent_node, level, "folder") for folder in folders]
        file_entries = [make_entry(file_entry, parent_node, level, "file") for file_entry in files]

        children = _apply_sorting_and_limits(
            folder_entries,
            file_entries,
            folders_first=folders_first,
            sort=sort,
            max_folders=max_folders,
            max_files=max_files,
            directory_node=parent_node,
        )

        parent_node.items = children
        nodes_in_order.extend(children)

        if max_lines and limit_level is None and len(nodes_in_order) >= max_lines:
            limit_level = level

        for child in children:
            if child.item_type != "folder":
                continue
            if max_depth and level >= max_depth:
                continue
            if limit_level is not None and level >= limit_level:
                continue
            child_abs = os.path.join(current_dir, child.name)
            queue.append((child, child_abs, level + 1))

    pruned_nodes: list[_TreeEntry] = nodes_in_order
    if max_lines and limit_level is not None:
        _prune_nested_children(
            root_node,
            lambda entry: entry.level <= limit_level,
        )
        pruned_nodes = [node for node in nodes_in_order if node.level <= limit_level]

    visible_nodes: list[_TreeEntry]
    if max_lines and limit_level is None:
        visible_nodes = pruned_nodes[:max_lines]
    else:
        visible_nodes = pruned_nodes

    visible_ids = {id(node) for node in visible_nodes}
    if visible_ids:
        _prune_to_visible(root_node, visible_ids)

    _mark_last_flags(root_node)
    _refresh_render_metadata(root_node)

    def iter_visible() -> Iterable[_TreeEntry]:
        for node in _iter_depth_first(root_node.items or []):
            if not visible_ids or id(node) in visible_ids:
                yield node

    if output_mode == OUTPUT_MODE_STRING:
        display_name = relative_path.strip() or root_name
        root_line = f"{display_name.rstrip(os.sep)}/"
        lines = [root_line]
        for node in iter_visible():
            lines.append(node.text)
        return "\n".join(lines)

    if output_mode == OUTPUT_MODE_FLAT:
        return _build_tree_items_flat(list(iter_visible()))

    return _to_nested_structure(root_node.items or [])


@dataclass(slots=True)
class _TreeEntry:
    name: str
    level: int
    item_type: Literal["file", "folder", "comment"]
    created: datetime
    modified: datetime
    parent: Optional["_TreeEntry"] = None
    items: Optional[list["_TreeEntry"]] = None
    is_last: bool = False
    rel_path: str = ""
    text: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "level": self.level,
            "type": self.item_type,
            "created": self.created,
            "modified": self.modified,
            "text": self.text,
            "items": [child.as_dict() for child in self.items] if self.items is not None else None,
        }


def _normalize_relative_path(path: str) -> str:
    normalized = path.replace(os.sep, "/")
    if normalized in {".", ""}:
        return ""
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _directory_has_visible_entries(
    directory: str,
    root_abs_path: str,
    ignore_spec: PathSpec,
    cache: dict[str, bool],
    max_depth_remaining: int,
) -> bool:
    if max_depth_remaining == 0:
        return False

    cached = cache.get(directory)
    if cached is not None:
        return cached

    try:
        with os.scandir(directory) as iterator:
            for entry in iterator:
                rel_path = os.path.relpath(entry.path, root_abs_path)
                rel_posix = _normalize_relative_path(rel_path)
                is_dir = entry.is_dir(follow_symlinks=False)

                if is_dir:
                    ignored = ignore_spec.match_file(rel_posix) or ignore_spec.match_file(f"{rel_posix}/")
                    if ignored:
                        next_depth = max_depth_remaining - 1 if max_depth_remaining > 0 else -1
                        if next_depth == 0:
                            continue
                        if _directory_has_visible_entries(
                            entry.path,
                            root_abs_path,
                            ignore_spec,
                            cache,
                            next_depth,
                        ):
                            cache[directory] = True
                            return True
                        continue
                else:
                    if ignore_spec.match_file(rel_posix):
                        continue

                cache[directory] = True
                return True
    except FileNotFoundError:
        cache[directory] = False
        return False

    cache[directory] = False
    return False


def _create_summary_comment(parent: _TreeEntry, noun: str, count: int) -> _TreeEntry:
    label = noun
    if count == 1 and noun.endswith("s"):
        label = noun[:-1]
    elif count > 1 and not noun.endswith("s"):
        label = f"{noun}s"
    return _TreeEntry(
        name=f"{count} more {label}",
        level=parent.level + 1,
        item_type="comment",
        created=parent.created,
        modified=parent.modified,
        parent=parent,
        items=None,
        rel_path=f"{parent.rel_path}#summary:{noun}:{count}",
    )


def _prune_nested_children(node: _TreeEntry, predicate: Callable[[_TreeEntry], bool]) -> None:
    if node.items is None:
        return
    pruned: list[_TreeEntry] = []
    for child in node.items:
        if predicate(child):
            _prune_nested_children(child, predicate)
            pruned.append(child)
    node.items = pruned


def _prune_to_visible(node: _TreeEntry, visible_ids: set[int]) -> None:
    if node.items is None:
        return
    filtered: list[_TreeEntry] = []
    for child in node.items:
        if not visible_ids or id(child) in visible_ids:
            _prune_to_visible(child, visible_ids)
            filtered.append(child)
    node.items = filtered


def _mark_last_flags(node: _TreeEntry) -> None:
    if node.items is None:
        return
    total = len(node.items)
    for index, child in enumerate(node.items):
        child.is_last = index == total - 1
        _mark_last_flags(child)


def _refresh_render_metadata(node: _TreeEntry) -> None:
    if node.items is None:
        return
    for child in node.items:
        child.text = _format_line(child)
        _refresh_render_metadata(child)


def _resolve_ignore_patterns(ignore: str | None, root_abs_path: str) -> Optional[PathSpec]:
    if ignore is None:
        return None

    content: str
    if ignore.startswith("file:"):
        reference = ignore[5:]
        if reference.startswith("///"):
            reference_path = reference[2:]
        elif reference.startswith("//"):
            reference_path = os.path.join(root_abs_path, reference[2:])
        elif reference.startswith("/"):
            reference_path = reference
        else:
            reference_path = os.path.join(root_abs_path, reference)

        try:
            with open(reference_path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Ignore file not found: {reference_path}") from exc
    else:
        content = ignore

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not lines:
        return None

    return PathSpec.from_lines("gitwildmatch", lines)


def _list_directory_children(
    directory: str,
    root_abs_path: str,
    ignore_spec: Optional[PathSpec],
    *,
    max_depth_remaining: int,
    cache: dict[str, bool],
) -> tuple[list[os.DirEntry], list[os.DirEntry]]:
    folders: list[os.DirEntry] = []
    files: list[os.DirEntry] = []

    try:
        with os.scandir(directory) as iterator:
            for entry in iterator:
                if entry.name in (".", ".."):
                    continue
                rel_path = os.path.relpath(entry.path, root_abs_path)
                rel_posix = _normalize_relative_path(rel_path)
                is_directory = entry.is_dir(follow_symlinks=False)

                if ignore_spec:
                    if is_directory:
                        ignored = ignore_spec.match_file(rel_posix) or ignore_spec.match_file(f"{rel_posix}/")
                        if ignored:
                            if _directory_has_visible_entries(
                                entry.path,
                                root_abs_path,
                                ignore_spec,
                                cache,
                                max_depth_remaining - 1,
                            ):
                                folders.append(entry)
                            continue
                    else:
                        if ignore_spec.match_file(rel_posix):
                            continue

                if is_directory:
                    folders.append(entry)
                else:
                    files.append(entry)
    except FileNotFoundError:
        return ([], [])

    return (folders, files)


def _apply_sorting_and_limits(
    folders: list[_TreeEntry],
    files: list[_TreeEntry],
    *,
    folders_first: bool,
    sort: tuple[str, str],
    max_folders: int | None,
    max_files: int | None,
    directory_node: _TreeEntry,
) -> list[_TreeEntry]:
    sort_key, sort_dir = sort
    reverse = sort_dir == SORT_DESC

    def key_fn(node: _TreeEntry):
        if sort_key == SORT_BY_NAME:
            return node.name.casefold()
        if sort_key == SORT_BY_CREATED:
            return node.created
        return node.modified

    folders_sorted = sorted(folders, key=key_fn, reverse=reverse)
    files_sorted = sorted(files, key=key_fn, reverse=reverse)
    combined: list[_TreeEntry] = []

    def append_group(group: list[_TreeEntry], limit: int | None, noun: str) -> None:
        if limit == 0:
            limit = None
        if not group:
            return
        if limit is None:
            combined.extend(group)
            return

        limit = max(limit, 0)
        visible = group[:limit]
        combined.extend(visible)

        overflow = group[limit:]
        if not overflow:
            return

        if len(overflow) == 1 and limit > 0:
            combined.append(overflow[0])
            return

        combined.append(
            _create_summary_comment(
                directory_node,
                noun,
                len(overflow),
            )
        )

    if folders_first:
        append_group(folders_sorted, max_folders, "folder")
        append_group(files_sorted, max_files, "file")
    else:
        append_group(files_sorted, max_files, "file")
        append_group(folders_sorted, max_folders, "folder")

    return combined


def _format_line(node: _TreeEntry) -> str:
    segments: list[str] = []
    ancestor = node.parent
    while ancestor and ancestor.parent is not None:
        segments.append("    " if ancestor.is_last else "│   ")
        ancestor = ancestor.parent
    segments.reverse()

    connector = "└── " if node.is_last else "├── "
    if node.item_type == "folder":
        label = f"{node.name}/"
    elif node.item_type == "comment":
        label = f"# {node.name}"
    else:
        label = node.name

    return "".join(segments) + connector + label


def _build_tree_items_flat(items: Sequence[_TreeEntry]) -> list[dict]:
    return [
        {
            "name": node.name,
            "level": node.level,
            "type": node.item_type,
            "created": node.created,
            "modified": node.modified,
            "text": node.text,
            "items": None,
        }
        for node in items
    ]


def _to_nested_structure(items: Sequence[_TreeEntry]) -> list[dict]:
    def convert(node: _TreeEntry) -> dict:
        children = None
        if node.items is not None:
            children = [convert(child) for child in node.items]
        return {
            "name": node.name,
            "level": node.level,
            "type": node.item_type,
            "created": node.created,
            "modified": node.modified,
            "text": node.text,
            "items": children,
        }

    return [convert(item) for item in items]


def _iter_depth_first(items: Sequence[_TreeEntry]) -> Iterable[_TreeEntry]:
    for node in items:
        yield node
        if node.items:
            yield from _iter_depth_first(node.items)
