from __future__ import annotations

from pathlib import Path
from typing import List

from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers import projects
from python.helpers import skills as skills_helper
from python.helpers import frameworks


class SkillsTool(Tool):
    """
    Manage and use SKILL.md-based Skills (Anthropic open standard).

    Methods (tool_args.method):
      - list
      - search (query)
      - load (skill_name)
      - read_file (skill_name, file_path)

    Script execution is handled by code_execution_tool directly.
    """

    def _get_project_name(self) -> str | None:
        ctx = getattr(self.agent, "context", None)
        return projects.get_context_project_name(ctx) if ctx else None

    def _get_framework_id(self) -> str | None:
        try:
            framework = frameworks.get_active_framework(self.agent.context)
            return framework.id if framework else None
        except Exception:
            return None
    async def execute(self, **kwargs) -> Response:
        method = (
            (kwargs.get("method") or self.args.get("method") or self.method or "")
            .strip()
            .lower()
        )

        try:
            if method == "list":
                return Response(message=self._list(), break_loop=False)
            if method == "search":
                query = str(kwargs.get("query") or "").strip()
                return Response(message=self._search(query), break_loop=False)
            if method == "load":
                skill_name = str(kwargs.get("skill_name") or "").strip()
                return Response(message=self._load(skill_name), break_loop=False)
            if method == "read_file":
                skill_name = str(kwargs.get("skill_name") or "").strip()
                file_path = str(kwargs.get("file_path") or "").strip()
                return Response(message=self._read_file(skill_name, file_path), break_loop=False)

            return Response(
                message=(
                    "Error: missing/invalid 'method'. Supported methods: "
                    "list, search, load, read_file."
                ),
                break_loop=False,
            )
        except Exception as e:  # keep tool robust; return error instead of crashing loop
            return Response(message=f"Error in skills_tool: {e}", break_loop=False)

    def _list(self) -> str:
        skills = skills_helper.list_skills(
            include_content=False,
            dedupe=True,
            project_name=self._get_project_name(),
            framework_id=self._get_framework_id(),
        )
        if not skills:
            return (
                "No skills found. Expected SKILL.md files under: "
                "usr/skills/{custom,default} or project .a0proj/skills."
            )

        # Stable output: sort by name
        skills_sorted = sorted(skills, key=lambda s: (s.name.lower(), s.source))

        lines: List[str] = []
        lines.append(f"Available skills ({len(skills_sorted)}):")
        for s in skills_sorted:
            tags = f" tags={','.join(s.tags)}" if s.tags else ""
            ver = f" v{s.version}" if s.version else ""
            desc = (s.description or "").strip()
            if len(desc) > 200:
                desc = desc[:200].rstrip() + "…"
            lines.append(f"- {s.name}{ver} [{s.source}]{tags}: {desc}")
        lines.append("")
        lines.append("Tip: use skills_tool method=search or method=load for details.")
        return "\n".join(lines)

    def _search(self, query: str) -> str:
        if not query:
            return "Error: 'query' is required for method=search."

        results = skills_helper.search_skills(
            query,
            limit=25,
            project_name=self._get_project_name(),
            framework_id=self._get_framework_id(),
        )
        if not results:
            return f"No skills matched query: {query!r}"

        lines: List[str] = []
        lines.append(f"Skills matching {query!r} ({len(results)}):")
        for s in results:
            desc = (s.description or "").strip()
            if len(desc) > 200:
                desc = desc[:200].rstrip() + "…"
            lines.append(f"- {s.name} [{s.source}]: {desc}")
        lines.append("")
        lines.append("Tip: use skills_tool method=load skill_name=<name> to load full instructions.")
        return "\n".join(lines)

    def _load(self, skill_name: str) -> str:
        if not skill_name:
            return "Error: 'skill_name' is required for method=load."

        skill = skills_helper.find_skill(
            skill_name,
            include_content=True,
            project_name=self._get_project_name(),
            framework_id=self._get_framework_id(),
        )
        if not skill:
            return f"Error: skill not found: {skill_name!r}. Try skills_tool method=list or method=search."

        # Enumerate files under the skill directory for progressive disclosure
        referenced_files = self._list_skill_files(skill.path, max_files=80)
        rel_skill_dir = Path(files.deabsolute_path(str(skill.path)))
        if self.agent.config.code_exec_ssh_enabled:
            runtime_path = files.normalize_a0_path(str(skill.path))
        else:
            runtime_path = str(skill.path)

        lines: List[str] = []
        lines.append(f"Skill: {skill.name}")
        lines.append(f"Source: {skill.source}")
        lines.append(f"Path: {rel_skill_dir}")
        lines.append(f"Runtime path: {runtime_path}")
        if skill.version:
            lines.append(f"Version: {skill.version}")
        if skill.author:
            lines.append(f"Author: {skill.author}")
        if skill.license:
            lines.append(f"License: {skill.license}")
        if skill.compatibility:
            lines.append(f"Compatibility: {skill.compatibility}")
        if skill.tags:
            lines.append(f"Tags: {', '.join(skill.tags)}")
        if skill.allowed_tools:
            lines.append(f"Allowed tools: {', '.join(skill.allowed_tools)}")
        if skill.triggers:
            lines.append(f"Triggers: {', '.join(skill.triggers)}")

        lines.append("")
        if skill.description:
            lines.append("Description:")
            lines.append(skill.description.strip())
            lines.append("")

        lines.append("Content (SKILL.md body):")
        lines.append(skill.content.strip() or "(empty)")
        lines.append("")

        if referenced_files:
            lines.append("Files in skill directory (use skills_tool method=read_file to open):")
            for p in referenced_files:
                lines.append(f"- {p}")
        else:
            lines.append("No additional files found in skill directory.")

        return "\n".join(lines)

    def _read_file(self, skill_name: str, file_path: str) -> str:
        if not skill_name:
            return "Error: 'skill_name' is required for method=read_file."
        if not file_path:
            return "Error: 'file_path' is required for method=read_file."

        skill = skills_helper.find_skill(
            skill_name,
            include_content=False,
            project_name=self._get_project_name(),
            framework_id=self._get_framework_id(),
        )
        if not skill:
            return f"Error: skill not found: {skill_name!r}."

        try:
            target = skills_helper.safe_path_within_dir(skill.path, file_path)
        except Exception as e:
            return f"Error: invalid file_path: {e}"

        if not target.exists() or not target.is_file():
            return f"Error: file not found: {file_path!r} (within skill {skill.name})"

        # Basic binary guard: if null byte present, do not dump
        content = target.read_bytes()
        if b"\x00" in content[:4096]:
            return f"Error: file appears to be binary; refusing to print raw bytes ({file_path})."

        text = content.decode("utf-8", errors="replace")
        return f"File: {file_path}\n\n{text}"

    def _list_skill_files(self, skill_dir: Path, *, max_files: int = 80) -> List[str]:
        if not skill_dir.exists():
            return []

        results: List[str] = []

        preferred_dirs = ["scripts", "references", "assets", "templates", "docs"]

        # 1) Root-level files (excluding SKILL.md)
        try:
            for p in sorted(skill_dir.iterdir(), key=lambda x: x.name):
                if len(results) >= max_files:
                    return results
                if p.name.startswith("."):
                    continue
                if p.is_file():
                    if p.name == "SKILL.md":
                        continue
                    results.append(p.name)
        except Exception:
            pass

        # 2) Preferred optional directories (one level deep)
        for dname in preferred_dirs:
            dpath = skill_dir / dname
            if not dpath.exists() or not dpath.is_dir():
                continue
            try:
                for p in sorted(dpath.iterdir(), key=lambda x: x.name):
                    if len(results) >= max_files:
                        return results
                    if p.name.startswith("."):
                        continue
                    if p.is_file():
                        results.append(f"{dname}/{p.name}")
                    elif p.is_dir():
                        # Show one nested level (common in assets/templates/*)
                        nested_added = False
                        try:
                            for sub in sorted(p.iterdir(), key=lambda x: x.name):
                                if sub.name.startswith("."):
                                    continue
                                if sub.is_file():
                                    results.append(f"{dname}/{p.name}/{sub.name}")
                                    nested_added = True
                                    break
                        except Exception:
                            pass
                        if not nested_added:
                            results.append(f"{dname}/{p.name}/")
            except Exception:
                continue

        # 3) Other directories (one level deep)
        try:
            for p in sorted(skill_dir.iterdir(), key=lambda x: x.name):
                if len(results) >= max_files:
                    return results
                if p.name.startswith(".") or p.name in preferred_dirs:
                    continue
                if p.is_dir():
                    for sub in sorted(p.iterdir(), key=lambda x: x.name):
                        if len(results) >= max_files:
                            return results
                        if sub.name.startswith("."):
                            continue
                        if sub.is_file():
                            results.append(f"{p.name}/{sub.name}")
        except Exception:
            pass

        return results


