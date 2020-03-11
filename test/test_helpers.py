import git
import pytest
from typing import Callable
from pathlib import Path
from smartsquash import helpers


def test_get_repo_works_in_subdir(repository: git.Repo, commit_files: Callable):
    commit_files(repository, ["test.txt"], "whatever")
    commit_files(repository, ["test.txt"], "even other content")
    path: Path = Path(Path(repository.working_dir) / "test")
    path.mkdir()
    assert isinstance(helpers.get_repo(str(path), "master"), git.Repo) is True


def test_get_repo_invalid(repository: git.Repo, commit_files: Callable):
    target_branch = "master"
    commit_files(repository, ["test.txt"], "whatever")
    repository.head.reference = repository.heads["master"]
    with pytest.raises(SystemExit):
        helpers.get_repo(repository.working_dir, target_branch)


def test_get_repo_path_not_exist(tmp_path: str):
    with pytest.raises(SystemExit):
        helpers.get_repo(f"{tmp_path}/invalid", "master")


def test_get_repo_not_a_git_repo(tmp_path: str):
    with pytest.raises(SystemExit):
        helpers.get_repo(tmp_path, "master")


def test_retrieve_commits(repository: git.Repo, commit_files: Callable):
    target_branch = "master"
    assert len(helpers.retrieve_commits(repository, target_branch)) == 0
    commit_files(repository, ["test.txt"], "test.txt")
    assert len(helpers.retrieve_commits(repository, target_branch)) == 1
    # create merge commit. Should not show up
    repository.create_head("new-merge")
    repository.head.reference = repository.heads["new-merge"]
    commit_files(repository, ["test.sh"], "echo whatever")
    repository.head.reference = repository.heads["feature-branch"]
    repository.git.merge("new-merge")
    assert len(helpers.retrieve_commits(repository, target_branch)) == 2


def test_files_changed_by_commit_1(repository: git.Repo, commit_files: Callable):
    changed_1 = sorted(["test.txt"])
    changed_2 = sorted(["test.txt", "whatever.img"])
    changed_3 = sorted(["test3.txt", "whatever.img", "test.txt"])
    commit_1: git.Commit = commit_files(repository, changed_1, "whatever")
    commit_2: git.Commit = commit_files(repository, changed_2, "whatever2")
    commit_3: git.Commit = commit_files(repository, changed_3, "whatever3")
    assert (
        helpers.files_changed_by_commit(repository.working_dir, commit_1.hexsha)
        == changed_1
    )
    assert (
        helpers.files_changed_by_commit(repository.working_dir, commit_2.hexsha)
        == changed_2
    )
    assert (
        helpers.files_changed_by_commit(repository.working_dir, commit_3.hexsha)
        == changed_3
    )


def test_repo_target_branch_invalid_message(
    repository: git.Repo, commit_files: Callable
):
    commit_files(repository, ["test.txt"], "whatever")
    repository.head.reference = repository.heads["master"]
    assert helpers.get_repo_invalid_message(repository, "master") == str(
        helpers.ErrorMessage.TARGET_EQUALS_CURRENT
    )
