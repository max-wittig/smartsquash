import git
import pytest
from smartsquash import helpers, fixup
from typing import Callable, Dict, Set
from pathlib import Path


def test_run_fixup_one_commit_add_files(
    repository: git.Repo, make_files: Callable, commit_files: Callable
):
    commit1: git.Commit = commit_files(repository, ["test.txt"], "content")
    make_files(repository, ["test.txt"], "content-changed")
    target_branch: str = "master"
    fixup.run_fixup(repository, target_branch, commit1.hexsha, True, False)
    assert len(helpers.retrieve_commits(repository, target_branch)) == 1
    assert (
        open(Path(repository.working_dir) / "test.txt", "r").read() == "content-changed"
    )


def test_run_fixup_tracked_files(
    repository: git.Repo, make_files: Callable, commit_files: Callable
):
    commit1: git.Commit = commit_files(repository, ["test.txt"], "content")
    make_files(repository, ["test.txt"], "content-changed")
    repository.index.add(["test.txt"])
    target_branch: str = "master"
    fixup.run_fixup(repository, target_branch, commit1.hexsha, False, False)
    assert len(helpers.retrieve_commits(repository, target_branch)) == 1
    assert repository.is_dirty() is False


def test_get_closest_change_commit():
    commit_changed_files: Dict[str, Set[str]] = {
        "000": {"something.txt"},
        "123": {"test.txt", "other.txt"},
        "456": {"test.txt"},
        "678": {"something-else.txt"},
    }
    files_changed: Set[str] = {"test.txt"}
    assert fixup.get_closest_change_commit(files_changed, commit_changed_files) == "123"


def test_get_closest_change_commit_not_found():
    commit_changed_files: Dict[str, Set[str]] = {
        "000": {"something.txt"},
        "123": {"test.txt", "other.txt"},
        "456": {"test.txt"},
        "678": {"something-else.txt"},
    }
    files_changed: Set[str] = {"not-found.txt"}
    assert fixup.get_closest_change_commit(files_changed, commit_changed_files) is None


@pytest.mark.parametrize(
    "changed_files", [(["README.md"]), (["README.md", "LICENSE.md"]), ([])]
)
def test_get_files_changed_in_staging(
    repository: git.Repo, make_files: Callable, changed_files
):
    make_files(repository, changed_files, "content")
    repository.index.add(changed_files)
    result_changed_files: Set[str] = fixup.get_files_changed_in_staging(repository)
    assert len(result_changed_files) == len(changed_files)
    assert sorted(list(result_changed_files)) == sorted(changed_files)
