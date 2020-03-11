import git
import re
import unittest.mock
from smartsquash import sq, helpers
from typing import Callable, List
from pathlib import Path


def test_squash(repository: git.Repo, commit_files: Callable):
    target_branch = "master"
    commit_files(repository, ["test.txt"], "whatever")
    commit_files(repository, ["test.txt"], "even other content")
    commits_before = sq.retrieve_commits(repository, target_branch)
    assert len(commits_before) == 2
    sq.squash(target_branch, repository, False)
    commits_after = helpers.retrieve_commits(repository, target_branch)
    assert len(commits_after) == 1


def test_squash_dry(repository: git.Repo, commit_files: Callable):
    target_branch = "master"
    commit_files(repository, ["test.txt"], "whatever")
    commit_files(repository, ["test.txt"], "even other content")
    commits_before = helpers.retrieve_commits(repository, target_branch)
    assert (
        len(commits_before)
        == len(helpers.retrieve_commits(repository, target_branch))
        == 2
    )


def test_fixup_files_repo_not_dirty(
    repository: git.Repo, make_files: Callable, commit_files: Callable
):
    commit_files(repository, ["test.txt"], "content")
    target_branch: str = "master"
    assert sq.fixup(target_branch, repository, True, False) is False
    assert len(helpers.retrieve_commits(repository, target_branch)) == 1
    assert open(Path(repository.working_dir) / "test.txt", "r").read() == "content"


def test_fixup_files(
    repository: git.Repo, make_files: Callable, commit_files: Callable
):
    commit_files(repository, ["test.txt"], "stuff")
    make_files(repository, ["test.txt"], "stuff1")
    repository.index.add("test.txt")
    target_branch: str = "master"
    assert sq.fixup(target_branch, repository, True, False) is True
    assert len(helpers.retrieve_commits(repository, target_branch)) == 1


def test_fixup_multiple_commits_with_in_between(
    repository: git.Repo, make_files: Callable, commit_files: Callable
):
    commit_files(repository, ["test.txt"], "original", message="first")
    commit_files(repository, ["test2.txt"], "modified", message="second")
    make_files(repository, ["test.txt"], "also changed")
    target_branch: str = "master"
    assert sq.fixup(target_branch, repository, True, False) is True
    commits: List[git.Commit] = helpers.retrieve_commits(
        repository, target_branch, reverse=False
    )
    assert len(commits) == 2
    assert re.match(r"^first", commits[1].message) is not None
    assert open(Path(repository.working_dir) / "test.txt", "r").read() == "also changed"


def test_fixup_multiple_commits(
    repository: git.Repo, make_files: Callable, commit_files: Callable
):
    commit_files(repository, ["test.txt"], "original", message="first")
    commit_files(repository, ["test.txt"], "modified after", message="second")
    make_files(repository, ["test.txt"], "also changed")
    target_branch: str = "master"
    assert sq.fixup(target_branch, repository, True, False) is True
    commits: List[git.Commit] = helpers.retrieve_commits(repository, target_branch)
    assert len(commits) == 2
    assert open(Path(repository.working_dir) / "test.txt", "r").read() == "also changed"


def test_fixup_into_larger_commit(
    repository: git.Repo, make_files: Callable, commit_files: Callable
):
    git.Commit = commit_files(
        repository, ["test.txt", "LICENSE.md", "README.md"], "original", message="first"
    )
    git.Commit = commit_files(
        repository, ["hello.xyz"], "modified after", message="second"
    )
    git.Commit = commit_files(
        repository, ["CONTRIBUTING.md"], "modified after", message="second"
    )
    make_files(repository, ["LICENSE.md"], "Some license change")
    target_branch: str = "master"
    assert sq.fixup(target_branch, repository, True, False) is True
    commits: List[git.Commit] = helpers.retrieve_commits(repository, target_branch)
    assert len(commits) == 3
    assert (
        open(Path(repository.working_dir) / "LICENSE.md", "r").read()
        == "Some license change"
    )
