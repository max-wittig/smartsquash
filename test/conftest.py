import pytest
import git
import uuid
from pathlib import Path
from typing import List, Optional, Callable


def add_random_files(repo: git.Repo, files_added=5, added_per_commit=1):
    files = [
        f"file-{repo.active_branch}-{i}-{str(uuid.uuid4())}"
        for i in range(0, files_added)
    ]
    for file in files:
        path = Path(repo.working_dir) / file
        for i in range(0, added_per_commit):
            real_path = f"{path.absolute()}-commit-{i}"
            with open(real_path, "w") as f:
                f.write(str(uuid.uuid4()))
            repo.index.add([real_path])
        repo.index.commit(str(uuid.uuid4()))


@pytest.fixture
def make_files() -> Callable:
    def _make_files(repo: git.Repo, files: List[str], content: str):
        for file in files:
            with open(Path(repo.working_dir) / file, "w") as f:
                f.write(content)

    return _make_files


@pytest.fixture
def commit_files(make_files) -> Callable:
    def _commit_files(
        repo: git.Repo, files: List[str], content: str, message: Optional[str] = None,
    ) -> git.Commit:
        previous_branch = repo.head.reference
        make_files(repo, files, content)
        repo.index.add(files)
        commit: git.Commit = repo.index.commit(message or f"Added {','.join(files)}")
        repo.head.reference = previous_branch
        return commit

    return _commit_files


@pytest.fixture
def repository(tmp_path) -> git.Repo:
    repo = git.Repo.init(tmp_path)
    add_random_files(repo)
    repo.create_head("feature-branch")
    repo.head.reference = repo.heads["feature-branch"]
    return repo
