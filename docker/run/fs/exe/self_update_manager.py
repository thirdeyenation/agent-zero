#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


OFFICIAL_REPO_URL = os.environ.get(
    "A0_SELF_UPDATE_REMOTE_URL",
    "https://github.com/agent0ai/agent-zero.git",
)
REPO_DIR = Path("/a0")
TRIGGER_FILE = Path("/exe/a0-self-update.yaml")
STATUS_FILE = Path("/exe/a0-self-update-status.yaml")
LOG_FILE = Path("/exe/a0-self-update.log")
DEFAULT_HEALTH_URL = os.environ.get(
    "A0_SELF_UPDATE_HEALTH_URL",
    "http://127.0.0.1:80/api/health",
)
DEFAULT_HEALTH_TIMEOUT_SECONDS = int(
    os.environ.get("A0_SELF_UPDATE_HEALTH_TIMEOUT_SECONDS", "120")
)
DEFAULT_HEALTH_POLL_INTERVAL_SECONDS = float(
    os.environ.get("A0_SELF_UPDATE_HEALTH_POLL_INTERVAL_SECONDS", "2")
)


def now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class AttemptLogger:
    def __init__(self, path: Path):
        self.path = path

    def reset(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def log(self, message: str = "") -> None:
        line = f"[{now_iso()}] {message}".rstrip()
        print(f"[a0-self-update] {message}", flush=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def log_block(self, title: str, content: str) -> None:
        cleaned = content.rstrip()
        self.log(f"{title}:")
        if not cleaned:
            self.log("(empty)")
            return
        with self.path.open("a", encoding="utf-8") as handle:
            for line in cleaned.splitlines():
                handle.write(f"    {line}\n")


class NullLogger:
    def reset(self) -> None:
        return

    def log(self, message: str = "") -> None:
        return

    def log_block(self, title: str, content: str) -> None:
        return


def load_yaml(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else None


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def write_status(payload: dict[str, Any]) -> None:
    write_yaml(STATUS_FILE, payload)


def git_output(repo_dir: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        check=True,
        text=True,
        capture_output=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    return completed.stdout.strip()


def normalize_describe_to_version(describe: str) -> str:
    match = re.fullmatch(r"(.+)-\d+-g[0-9a-f]+", describe)
    if match:
        return match.group(1)
    return describe


def get_repo_version_info(repo_dir: Path) -> dict[str, str]:
    describe = git_output(repo_dir, "describe", "--tags", "--always")
    commit = git_output(repo_dir, "rev-parse", "HEAD")
    return {
        "describe": describe,
        "short_tag": normalize_describe_to_version(describe),
        "commit": commit,
        "short_commit": commit[:7],
    }


def normalize_rel_path(value: str | Path) -> str:
    normalized = str(value).replace("\\", "/").strip("/")
    if normalized in {"", "."}:
        return ""
    while normalized.startswith("./"):
        normalized = normalized[2:]
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized.rstrip("/")


def is_protected_path(relative_path: str, protected_paths: set[str]) -> bool:
    normalized = normalize_rel_path(relative_path)
    if not normalized:
        return False
    return any(
        normalized == protected or normalized.startswith(f"{protected}/")
        for protected in protected_paths
    )


def list_protected_paths(repo_dir: Path) -> set[str]:
    output = git_output(
        repo_dir,
        "ls-files",
        "--others",
        "-i",
        "--exclude-standard",
        "--directory",
    )
    protected: set[str] = set()
    for raw_line in output.splitlines():
        normalized = normalize_rel_path(raw_line)
        if not normalized:
            continue
        current = Path(normalized)
        while True:
            candidate = normalize_rel_path(current.as_posix())
            if candidate:
                protected.add(candidate)
            if str(current.parent) in {"", "."}:
                break
            current = current.parent
    return protected


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
        return
    if path.exists():
        shutil.rmtree(path)


def sync_tree(source_dir: Path, target_dir: Path, *, protected_paths: set[str]) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    protected = {normalize_rel_path(path) for path in protected_paths if path}

    def _sync(src: Path, dst: Path, relative_root: str) -> None:
        source_entries = {item.name: item for item in src.iterdir()} if src.exists() else {}
        target_entries = {item.name: item for item in dst.iterdir()} if dst.exists() else {}

        for name, src_entry in source_entries.items():
            relative_path = normalize_rel_path(Path(relative_root, name).as_posix())
            if is_protected_path(relative_path, protected):
                continue

            dst_entry = dst / name
            if src_entry.is_symlink():
                link_target = os.readlink(src_entry)
                if dst_entry.is_symlink() and os.readlink(dst_entry) == link_target:
                    continue
                remove_path(dst_entry)
                os.symlink(link_target, dst_entry)
                continue

            if src_entry.is_dir():
                if dst_entry.exists() and not dst_entry.is_dir():
                    remove_path(dst_entry)
                dst_entry.mkdir(parents=True, exist_ok=True)
                _sync(src_entry, dst_entry, relative_path)
                try:
                    shutil.copystat(src_entry, dst_entry, follow_symlinks=False)
                except OSError:
                    pass
                continue

            if dst_entry.exists() and dst_entry.is_dir():
                remove_path(dst_entry)
            dst_entry.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_entry, dst_entry, follow_symlinks=False)

        for name, dst_entry in target_entries.items():
            relative_path = normalize_rel_path(Path(relative_root, name).as_posix())
            if name in source_entries:
                continue
            if is_protected_path(relative_path, protected):
                continue
            remove_path(dst_entry)

    _sync(source_dir, target_dir, "")


def sanitize_filename(name: str, default_name: str) -> str:
    raw = (name or "").strip()
    if not raw:
        raw = default_name
    raw = Path(raw).name
    raw = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip(".-") or default_name
    if not raw.lower().endswith(".zip"):
        raw = f"{raw}.zip"
    return raw


def resolve_backup_destination(
    directory: Path,
    filename: str,
    conflict_policy: str,
) -> Path:
    normalized_policy = conflict_policy.strip().lower()
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / filename
    if not destination.exists():
        return destination

    if normalized_policy == "overwrite":
        remove_path(destination)
        return destination
    if normalized_policy == "fail":
        raise FileExistsError(f"Backup file already exists: {destination}")
    if normalized_policy != "rename":
        raise ValueError("backup_conflict_policy must be rename, overwrite, or fail.")

    stem = destination.stem
    suffix = destination.suffix
    index = 2
    while True:
        candidate = directory / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def create_usr_backup(
    *,
    repo_dir: Path,
    backup_path: str,
    backup_name: str,
    conflict_policy: str,
    logger: AttemptLogger,
) -> Path:
    usr_dir = repo_dir / "usr"
    if not usr_dir.exists():
        raise FileNotFoundError(f"User directory not found: {usr_dir}")

    destination_dir = Path(backup_path)
    if not destination_dir.is_absolute():
        destination_dir = (repo_dir / destination_dir).resolve()
    else:
        destination_dir = destination_dir.resolve()
    destination_name = sanitize_filename(backup_name, "agent-zero-usr-backup.zip")
    destination = resolve_backup_destination(destination_dir, destination_name, conflict_policy)

    temp_fd, temp_path = tempfile.mkstemp(suffix=".zip")
    os.close(temp_fd)
    temporary_backup = Path(temp_path)

    try:
        with zipfile.ZipFile(
            temporary_backup,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
        ) as archive:
            for root, _, files in os.walk(usr_dir):
                root_path = Path(root)
                for filename in files:
                    source_file = root_path / filename
                    archive_name = Path("usr") / source_file.relative_to(usr_dir)
                    archive.write(source_file, archive_name.as_posix())

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(temporary_backup), str(destination))
        logger.log(f"Created usr backup at {destination}")
        return destination
    finally:
        if temporary_backup.exists():
            temporary_backup.unlink(missing_ok=True)


def run_command(command: list[str], *, cwd: Path | None, logger: AttemptLogger) -> None:
    logger.log(f"$ {' '.join(command)}")
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    if completed.stdout:
        logger.log_block("stdout", completed.stdout)
    if completed.stderr:
        logger.log_block("stderr", completed.stderr)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {completed.returncode}: {' '.join(command)}"
        )


def clone_release(branch: str, tag: str, destination: Path, logger: AttemptLogger) -> None:
    logger.log(f"Fetching branch {branch} and tag {tag} from {OFFICIAL_REPO_URL}")
    run_command(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            branch,
            "--single-branch",
            OFFICIAL_REPO_URL,
            str(destination),
        ],
        cwd=None,
        logger=logger,
    )
    run_command(
        [
            "git",
            "-C",
            str(destination),
            "fetch",
            "--depth",
            "1",
            "origin",
            f"refs/tags/{tag}:refs/tags/{tag}",
        ],
        cwd=None,
        logger=logger,
    )
    run_command(
        [
            "git",
            "-C",
            str(destination),
            "checkout",
            "--detach",
            f"refs/tags/{tag}",
        ],
        cwd=None,
        logger=logger,
    )


def launch_ui_process(repo_dir: Path, logger: AttemptLogger) -> subprocess.Popen[bytes]:
    prepare_script = repo_dir / "prepare.py"
    if prepare_script.exists():
        logger.log("Running prepare.py before UI start")
        run_command([sys.executable, str(prepare_script), "--dockerized=true"], cwd=repo_dir, logger=logger)
    else:
        logger.log("prepare.py not found, skipping prepare step")

    logger.log("Starting Agent Zero UI")
    return subprocess.Popen(
        [
            sys.executable,
            str(repo_dir / "run_ui.py"),
            "--dockerized=true",
            "--port=80",
            "--host=0.0.0.0",
        ],
        cwd=repo_dir,
    )


def wait_for_health(
    process: subprocess.Popen[bytes],
    *,
    health_url: str,
    timeout_seconds: int,
    poll_interval_seconds: float,
    expected_version: str | None = None,
    logger: AttemptLogger,
) -> tuple[bool, dict[str, Any] | str]:
    deadline = time.monotonic() + timeout_seconds
    last_error = "Health check did not return a successful response."

    while time.monotonic() < deadline:
        if process.poll() is not None:
            return (
                False,
                f"UI process exited with code {process.returncode} before passing the health check.",
            )
        try:
            request = urllib.request.Request(
                health_url,
                headers={"Cache-Control": "no-cache"},
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                body = response.read().decode("utf-8")
                payload = json.loads(body) if body else {}
                git_info = payload.get("gitinfo") or {}
                current_version = (git_info.get("short_tag") or "").strip()
                if expected_version and current_version and current_version != expected_version:
                    last_error = (
                        f"Health check responded, but version {current_version} does not match "
                        f"expected {expected_version}."
                    )
                elif response.status == 200:
                    logger.log(f"Health check passed at {health_url}")
                    return True, payload
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)

        time.sleep(poll_interval_seconds)

    return False, last_error


def terminate_process(process: subprocess.Popen[bytes], timeout_seconds: int = 20) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def wait_for_process(process: subprocess.Popen[bytes]) -> int:
    def forward_signal(signum, _frame) -> None:
        if process.poll() is None:
            process.send_signal(signum)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, forward_signal)
        except ValueError:
            pass

    return process.wait()


def record_result(
    *,
    status: str,
    message: str,
    request_data: dict[str, Any],
    source_info: dict[str, str],
    current_version: str,
    started_at: str,
    backup_zip_path: str = "",
    rollback_applied: bool = False,
    error: str = "",
) -> None:
    payload: dict[str, Any] = {
        "status": status,
        "message": message,
        "branch": str(request_data.get("branch", "")),
        "tag": str(request_data.get("tag", "")),
        "source_version": source_info["short_tag"],
        "source_commit": source_info["commit"],
        "current_version": current_version,
        "requested_at": str(request_data.get("requested_at", "")),
        "started_at": started_at,
        "finished_at": now_iso(),
        "log_file_path": str(LOG_FILE),
        "update_file_path": str(TRIGGER_FILE),
        "rollback_applied": rollback_applied,
    }
    if backup_zip_path:
        payload["backup_zip_path"] = backup_zip_path
    if error:
        payload["error"] = error
    write_status(payload)


def execute_pending_update(
    request_data: dict[str, Any],
    *,
    logger: AttemptLogger,
) -> subprocess.Popen[bytes]:
    source_info = get_repo_version_info(REPO_DIR)
    started_at = now_iso()
    protected_paths = list_protected_paths(REPO_DIR)
    temp_root = Path(tempfile.mkdtemp(prefix="a0-self-update-"))
    staging_repo = temp_root / "release"
    snapshot_dir = temp_root / "snapshot"
    backup_zip_path = ""
    repository_changed = False
    branch = str(request_data.get("branch", "")).strip()
    tag = str(request_data.get("tag", "")).strip()

    try:
        if not branch:
            raise ValueError("Update file is missing the branch field.")
        if not tag:
            raise ValueError("Update file is missing the tag field.")

        if bool(request_data.get("backup_usr", True)):
            backup_zip_path = str(
                create_usr_backup(
                    repo_dir=REPO_DIR,
                    backup_path=str(request_data.get("backup_path", "/a0/tmp/self-update-backups")),
                    backup_name=str(request_data.get("backup_name", "agent-zero-usr-backup.zip")),
                    conflict_policy=str(request_data.get("backup_conflict_policy", "rename")),
                    logger=logger,
                )
            )

        logger.log("Creating rollback snapshot")
        sync_tree(REPO_DIR, snapshot_dir, protected_paths=protected_paths)

        clone_release(branch, tag, staging_repo, logger)

        logger.log("Applying release into /a0 while preserving ignored paths")
        sync_tree(staging_repo, REPO_DIR, protected_paths=protected_paths)
        repository_changed = True

        current_info = get_repo_version_info(REPO_DIR)
        if current_info["short_tag"] != tag:
            raise RuntimeError(
                "Release sync completed but the repository version does not match the requested tag. "
                f"Expected {tag}, got {current_info['short_tag']}."
            )

        updated_process = launch_ui_process(REPO_DIR, logger)
        healthy, details = wait_for_health(
            updated_process,
            health_url=DEFAULT_HEALTH_URL,
            timeout_seconds=DEFAULT_HEALTH_TIMEOUT_SECONDS,
            poll_interval_seconds=DEFAULT_HEALTH_POLL_INTERVAL_SECONDS,
            expected_version=tag,
            logger=logger,
        )
        if healthy:
            record_result(
                status="success",
                message=f"Updated Agent Zero to branch {branch}, tag {tag}.",
                request_data=request_data,
                source_info=source_info,
                current_version=current_info["short_tag"],
                started_at=started_at,
                backup_zip_path=backup_zip_path,
                rollback_applied=False,
            )
            return updated_process

        logger.log(f"Updated UI failed health check, rolling back: {details}")
        terminate_process(updated_process)
        sync_tree(snapshot_dir, REPO_DIR, protected_paths=protected_paths)

        rollback_process = launch_ui_process(REPO_DIR, logger)
        rollback_healthy, rollback_details = wait_for_health(
            rollback_process,
            health_url=DEFAULT_HEALTH_URL,
            timeout_seconds=DEFAULT_HEALTH_TIMEOUT_SECONDS,
            poll_interval_seconds=DEFAULT_HEALTH_POLL_INTERVAL_SECONDS,
            expected_version=source_info["short_tag"],
            logger=logger,
        )

        if rollback_healthy:
            record_result(
                status="rolled_back",
                message=(
                    "Updated version failed its health check and the previous version was restored. "
                    f"Reason: {details}"
                ),
                request_data=request_data,
                source_info=source_info,
                current_version=source_info["short_tag"],
                started_at=started_at,
                backup_zip_path=backup_zip_path,
                rollback_applied=True,
                error=str(details),
            )
            return rollback_process

        terminate_process(rollback_process)
        record_result(
            status="rollback_failed",
            message=(
                "Updated version failed its health check and rollback also failed to become healthy."
            ),
            request_data=request_data,
            source_info=source_info,
            current_version=source_info["short_tag"],
            started_at=started_at,
            backup_zip_path=backup_zip_path,
            rollback_applied=True,
            error=f"Update error: {details}. Rollback error: {rollback_details}",
        )
        raise RuntimeError(str(rollback_details))
    except Exception as exc:
        if repository_changed and snapshot_dir.exists():
            logger.log(f"Restoring rollback snapshot after error: {exc}")
            sync_tree(snapshot_dir, REPO_DIR, protected_paths=protected_paths)

        record_result(
            status="failed" if not repository_changed else "rolled_back",
            message=str(exc),
            request_data=request_data,
            source_info=source_info,
            current_version=source_info["short_tag"],
            started_at=started_at,
            backup_zip_path=backup_zip_path,
            rollback_applied=repository_changed,
            error=str(exc),
        )
        logger.log(f"Update flow failed: {exc}")
        return launch_ui_process(REPO_DIR, logger)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def load_request_file() -> tuple[dict[str, Any] | None, str]:
    if not TRIGGER_FILE.exists():
        return None, ""
    raw_text = TRIGGER_FILE.read_text(encoding="utf-8")
    try:
        loaded = yaml.safe_load(raw_text)
        return (loaded if isinstance(loaded, dict) else None), raw_text
    finally:
        TRIGGER_FILE.unlink(missing_ok=True)


def docker_run_ui() -> int:
    request_data, raw_text = load_request_file()
    logger = AttemptLogger(LOG_FILE)
    quiet_logger = NullLogger()

    if request_data:
        logger.reset()
        logger.log(f"Consumed update file at {TRIGGER_FILE}")
        logger.log_block("Trigger file content", raw_text)

        try:
            current = get_repo_version_info(REPO_DIR)
            requested_tag = str(request_data.get("tag", "")).strip()
            if requested_tag and current["short_tag"] == requested_tag:
                logger.log(
                    "Requested tag already matches the installed version, skipping file replacement."
                )
                record_result(
                    status="skipped",
                    message="Requested tag already matches the installed version.",
                    request_data=request_data,
                    source_info=current,
                    current_version=current["short_tag"],
                    started_at=now_iso(),
                    rollback_applied=False,
                )
                process = launch_ui_process(REPO_DIR, logger)
            else:
                process = execute_pending_update(request_data, logger=logger)
        except Exception as exc:
            logger.log(f"Self-update bootstrap failed unexpectedly: {exc}")
            process = launch_ui_process(REPO_DIR, logger)
    elif raw_text:
        logger.reset()
        logger.log(f"Consumed invalid update file at {TRIGGER_FILE}")
        logger.log_block("Trigger file content", raw_text)
        source_info = get_repo_version_info(REPO_DIR)
        record_result(
            status="failed",
            message="Update file was not valid YAML.",
            request_data={},
            source_info=source_info,
            current_version=source_info["short_tag"],
            started_at=now_iso(),
            rollback_applied=False,
            error="Update file was not valid YAML.",
        )
        process = launch_ui_process(REPO_DIR, logger)
    else:
        process = launch_ui_process(REPO_DIR, quiet_logger)

    return wait_for_process(process)


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if args and args[0] not in {"docker-run-ui"}:
        print(f"Unknown command: {args[0]}", file=sys.stderr)
        return 1
    return docker_run_ui()


if __name__ == "__main__":
    raise SystemExit(main())
