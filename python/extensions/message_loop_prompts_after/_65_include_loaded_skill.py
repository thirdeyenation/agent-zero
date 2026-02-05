from pathlib import Path
from python.helpers.extension import Extension
from python.helpers import skills, files, file_tree, runtime
from agent import LoopData


DATA_NAME_LOADED_SKILL = "loaded_skill"


class IncludeLoadedSkill(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        skill_name = self.agent.data.get(DATA_NAME_LOADED_SKILL)
        if not skill_name:
            return

        # Load skill fresh each turn
        skill = skills.find_skill(skill_name, include_content=True, agent=self.agent)
        if not skill:
            return

        # Build skill block
        skill_block = self._build_skill_block(skill)

        # Add to persistent extras
        loop_data.extras_persistent["loaded_skill"] = self.agent.read_prompt(
            "agent.system.skill.loaded.md",
            skill=skill_block,
        )

    def _build_skill_block(self, skill: skills.Skill) -> str:
        """Build complete skill content with metadata, description, body, and files."""
        runtime_path = (
            files.normalize_a0_path(str(skill.path))
            if self.agent.config.code_exec_ssh_enabled
            else str(skill.path)
        )

        lines = [f"Skill: {skill.name}", f"Path: {runtime_path}"]

        # Metadata
        metadata = [
            ("Version", skill.version),
            ("Author", skill.author),
            ("License", skill.license),
            ("Compatibility", skill.compatibility),
            ("Tags", ", ".join(skill.tags) if skill.tags else None),
            ("Allowed tools", ", ".join(skill.allowed_tools) if skill.allowed_tools else None),
            ("Triggers", ", ".join(skill.triggers) if skill.triggers else None),
        ]
        lines.extend(f"{label}: {value}" for label, value in metadata if value)

        # Description and content
        if skill.description:
            lines.extend(["", "Description:", skill.description.strip()])

        lines.extend(["", "Content (SKILL.md body):", skill.content.strip() or "(empty)"])

        # File tree
        files_tree = self._get_skill_files(skill.path)
        lines.append("")
        if files_tree:
            lines.append("Files (use skills_tool method=read_file to open):")
            lines.append(files_tree)
        else:
            lines.append("No additional files found.")

        return "\n".join(lines)

    def _get_skill_files(self, skill_dir: Path) -> str:
        """Get file tree for skill directory."""
        if not skill_dir.exists():
            return ""

        tree = str(
            file_tree.file_tree(
                str(skill_dir),
                max_depth=10,
                folders_first=True,
                max_files=100,
                max_folders=100,
                output_mode="string",
                max_lines=300,
                ignore=files.read_file("conf/skill.default.gitignore"),
            )
        )

        if tree and runtime.is_development():
            runtime_path = files.normalize_a0_path(str(skill_dir))
            tree = tree.replace(str(skill_dir), runtime_path)

        return str(tree)
