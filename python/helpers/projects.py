from dataclasses import dataclass
import os
from typing import TypedDict

from torch import ne
from python.helpers import files, dirty_json
from python.helpers.print_style import PrintStyle

PROJECTS_PARENT_DIR = "tmp/projects"
PROJECTS_ARCHIVE_DIR = "tmp/projects-archived"
PROJECT_META_DIR = ".a0proj"
PROJECT_INSTRUCTIONS_DIR = "instructions"
PROJECT_HEADER_FILE = "project.json"


class BasicProjectData(TypedDict):
    title: str | None
    description: str | None
    instructions: str | None
    color: str | None


def get_projects_parent_folder():
    return files.get_abs_path(PROJECTS_PARENT_DIR)


def get_projects_archive_folder():
    return files.get_abs_path(PROJECTS_ARCHIVE_DIR)


def get_project_folder(name: str):
    return files.get_abs_path(get_projects_parent_folder(), name)


def get_archived_project_folder(name: str):
    return files.get_abs_path(get_projects_archive_folder(), name)


def archive_project(name: str):
    return files.move_dir_safe(
        get_project_folder(name), get_archived_project_folder(name)
    )


def unarchive_project(name: str):
    return files.move_dir_safe(
        get_archived_project_folder(name), get_project_folder(name)
    )


def delete_project(path: str):
    files.delete_dir(path)


async def create_project(name: str, data: BasicProjectData):
    new_name = files.create_dir_safe(get_project_folder(name))
    save_project_files(new_name, data)


async def update_project(path: str, data: BasicProjectData):
    current: BasicProjectData = load_basic_project_data(path)  # type: ignore
    current.update(data)
    save_project_files(path, current)


def load_basic_project_data(path: str) -> BasicProjectData:
    data = dirty_json.parse(
        files.read_file(
            files.get_abs_path(path, PROJECT_HEADER_FILE)
        )
    ) 
    return data # type: ignore


def save_project_files(path: str, data: BasicProjectData):
    # save project header file
    header = dirty_json.stringify(data)
    files.write_file(
        files.get_abs_path(path, PROJECT_HEADER_FILE), header
    )

async def get_active_projects_list():
    return await get_projects_list(get_projects_parent_folder())

async def get_archived_projects_list():
    return await get_projects_list(get_projects_archive_folder())

async def get_projects_list(parent_dir):
    projects = []

    # folders in project directory
    for name in os.listdir(parent_dir):
        try:
            path = os.path.join(parent_dir, name)
            if os.path.isdir(path):

                project_data = load_basic_project_data(path)

                projects.append({
                    "name": name,
                    "path": path,
                    "title": project_data.get("title", ""),
                    "description": project_data.get("description", ""),
                })
        except Exception as e:
            PrintStyle.error(f"Error loading project {name}: {str(e)}")

    # sort projects by name
    
    projects.sort(key=lambda x: x["name"])
    return projects
