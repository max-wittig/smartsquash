import git
import re
from smartsquash import helpers, sq, squash
from typing import List, Dict, Set, Callable


def test_get_commits_in_between(repository: git.Repo, commit_files: Callable):
    commit_1: git.Commit = commit_files(repository, ["test.txt"], "whatever")
    commit_2: git.Commit = commit_files(
        repository, ["test.txt", "stuff.txt"], "some other content"
    )
    commit_3: git.Commit = commit_files(
        repository, ["something.txt"], "even other content"
    )
    commit_4: git.Commit = commit_files(
        repository, ["another-one.txt"], "even other content"
    )
    commits: List[git.Commit] = sq.retrieve_commits(repository, "master")
    in_between: List[git.Commit] = squash.get_commits_in_between(
        commit_4, commit_1, commits
    )
    assert len(in_between) == 2
    assert in_between[0] == commit_2
    assert in_between[1] == commit_3


def test_has_relevant_files_changed_in_between_1(
    repository: git.Repo, commit_files: Callable
):
    commit_1 = commit_files(repository, ["test.txt"], "Some content")
    commit_2 = commit_files(repository, ["whatever.txt"], "Some content")
    commit_3 = commit_files(repository, ["another.txt"], "Some content")
    commit_4 = commit_files(repository, ["test.txt"], "Other content")
    commits = [commit_4, commit_3, commit_2, commit_1]
    commit_changed_files: Dict[str, Set[str]] = {
        commit_1.hexsha: {"test.txt"},
        commit_2.hexsha: {"whatever.txt"},
        commit_3.hexsha: {"another.txt"},
        commit_4.hexsha: {"test.txt"},
    }
    assert (
        squash.has_relevant_files_changed_in_between(
            commit_4, commit_1, commits, commit_changed_files
        )
        is False
    )


def test_has_relevant_files_changed_in_between_2(
    repository: git.Repo, commit_files: Callable
):
    commit_1 = commit_files(repository, ["test.txt"], "Some content")
    commit_2 = commit_files(repository, ["whatever.txt"], "Some content")
    commit_3 = commit_files(repository, ["another.txt", "test.txt"], "Some content")
    commit_4 = commit_files(repository, ["another.txt", "test.txt"], "Some")
    commit_5 = commit_files(repository, ["test.txt"], "Other content")
    commits = [commit_5, commit_4, commit_3, commit_2, commit_1]
    commit_changed_files: Dict[str, Set[str]] = {
        commit_1.hexsha: {"test.txt"},
        commit_2.hexsha: {"whatever.txt"},
        commit_3.hexsha: {"another.txt", "test.txt"},
        commit_4.hexsha: {"another.txt", "test.txt"},
        commit_5.hexsha: {"test.txt"},
    }
    assert (
        squash.has_relevant_files_changed_in_between(
            commit_5, commit_1, commits, commit_changed_files
        )
        is True
    )
    assert (
        squash.has_relevant_files_changed_in_between(
            commit_4, commit_3, commits, commit_changed_files
        )
        is False
    )


def test_commit_diff_empty(repository: git.Repo, commit_files: Callable):
    content = "old content"
    filename = "test.txt"
    # commit file to repo
    commit_a = commit_files(repository, [filename], content)
    # now write something else in file
    commit_b = commit_files(repository, [filename], "new content")
    # change file back
    commit_c = commit_files(repository, [filename], content)
    assert squash.commit_diff_empty(commit_a, commit_c)
    assert not squash.commit_diff_empty(commit_a, commit_b)
    assert not squash.commit_diff_empty(commit_b, commit_c)


def test_has_same_files():
    files_a: List[str] = ["test.txt", "README.md"]
    files_b: List[str] = ["README.md", "test.txt"]
    assert squash.has_same_files(files_a, files_b)
    files_b.append("Stuff.whatever")
    assert not squash.has_same_files(files_a, files_b)
    files_c: List[str] = ["1.txt", "2.txt", "3.txt"]
    assert not squash.has_same_files(files_a, files_c)


def test_get_rebase_data_1(repository: git.Repo, commit_files: Callable):
    commit_files(repository, ["test.txt"], "whatever")
    commit_files(repository, ["test.txt"], "some other content")
    commit_files(repository, ["test.txt"], "even other content")
    commit_files(repository, ["test.txt"], "wwaaaaa")
    commits = helpers.retrieve_commits(repository, "master")
    is_rebase, rebase_data = squash.get_rebase_data(commits)
    rebase_data = rebase_data.split("\n")
    assert is_rebase is True
    assert re.match(r"^pick\s.{7}\s.*", rebase_data[0])
    assert re.match(r"^fixup\s.{7}\s.*", rebase_data[1])
    assert re.match(r"^fixup\s.{7}\s.*", rebase_data[2])
    assert re.match(r"^fixup\s.{7}\s.*", rebase_data[3])


def test_get_rebase_data_2(repository: git.Repo, commit_files: Callable):
    commit_files(repository, ["test.txt"], "whatever")
    commit_files(repository, ["test.txt", "stuff.txt"], "some other content")
    commit_files(repository, ["test.txt"], "even other content")
    commits = helpers.retrieve_commits(repository, "master")
    is_rebase, rebase_data = squash.get_rebase_data(commits)
    rebase_data = rebase_data.split("\n")
    assert is_rebase is False
    assert re.match(r"^pick\s.{7}\s.*", rebase_data[0])
    assert re.match(r"^pick\s.{7}\s.*", rebase_data[1])
    assert re.match(r"^pick\s.{7}\s.*", rebase_data[2])


def test_get_rebase_data_3(repository: git.Repo, commit_files: Callable):
    commit_files(repository, ["test.txt", "stuff.txt"], "whatever")
    commit_files(repository, ["test.txt", "stuff.txt"], "some other content")
    commit_files(repository, ["test.txt"], "even other content")
    commits = helpers.retrieve_commits(repository, "master")
    is_rebase, rebase_data = squash.get_rebase_data(commits)
    rebase_data = rebase_data.split("\n")
    assert is_rebase is True
    assert re.match(r"^pick\s.{7}\s.*", rebase_data[0])
    assert re.match(r"^fixup\s.{7}\s.*", rebase_data[1])
    assert re.match(r"^pick\s.{7}\s.*", rebase_data[2])


def test_get_rebase_data_4(repository: git.Repo, commit_files: Callable):
    commit_1 = commit_files(repository, ["test.txt"], "whatever")
    commit_2 = commit_files(repository, ["whatever.img"], "some other content")
    commit_3 = commit_files(repository, ["test.txt"], "even other content")
    commits = helpers.retrieve_commits(repository, "master")
    is_rebase, rebase_data = squash.get_rebase_data(commits)
    rebase_data = rebase_data.split("\n")
    assert is_rebase is True
    assert re.match(rf"^pick\s{commit_1.hexsha[:7]}\s.*", rebase_data[0])
    assert re.match(rf"^fixup\s{commit_3.hexsha[:7]}\s.*", rebase_data[1])
    assert re.match(rf"^pick\s{commit_2.hexsha[:7]}\s.*", rebase_data[2])


def test_get_rebase_data_5(repository: git.Repo, commit_files: Callable):
    commit_1 = commit_files(repository, ["test.txt"], "whatever")
    commit_2 = commit_files(repository, ["whatever.img"], "some other content")
    commit_3 = commit_files(repository, ["test.txt"], "whatever2")
    commit_4 = commit_files(
        repository, ["whatever.img", "test.txt"], "some other content2"
    )
    commit_5 = commit_files(repository, ["test.txt"], "even other content")
    commits = helpers.retrieve_commits(repository, "master")
    is_rebase, rebase_data = squash.get_rebase_data(commits)
    rebase_data = rebase_data.split("\n")
    assert is_rebase is True
    assert re.match(rf"^pick\s{commit_1.hexsha[:7]}\s.*", rebase_data[0])
    assert re.match(rf"^fixup\s{commit_3.hexsha[:7]}\s.*", rebase_data[1])
    assert re.match(rf"^pick\s{commit_2.hexsha[:7]}\s.*", rebase_data[2])
    assert re.match(rf"^pick\s{commit_4.hexsha[:7]}\s.*", rebase_data[3])
    assert re.match(rf"^pick\s{commit_5.hexsha[:7]}\s.*", rebase_data[4])


def test_get_rebase_data_6(repository: git.Repo, commit_files: Callable):
    commit_1 = commit_files(
        repository, ["test.txt", "1.txt", "5.txt", "gdf.txt"], "whatever"
    )
    commit_2 = commit_files(repository, ["5.txt"], "some other content")
    commit_3 = commit_files(repository, ["test.txt"], "whatever2")
    commit_4 = commit_files(repository, ["5.txt", "test.txt"], "some other content2")
    commit_5 = commit_files(repository, ["test.txt"], "even other content")
    commits = helpers.retrieve_commits(repository, "master")
    is_rebase, rebase_data = squash.get_rebase_data(commits)
    rebase_data = rebase_data.split("\n")
    assert is_rebase is False
    assert re.match(rf"^pick\s{commit_1.hexsha[:7]}\s.*", rebase_data[0])
    assert re.match(rf"^pick\s{commit_2.hexsha[:7]}\s.*", rebase_data[1])
    assert re.match(rf"^pick\s{commit_3.hexsha[:7]}\s.*", rebase_data[2])
    assert re.match(rf"^pick\s{commit_4.hexsha[:7]}\s.*", rebase_data[3])
    assert re.match(rf"^pick\s{commit_5.hexsha[:7]}\s.*", rebase_data[4])


def test_get_commit_message_empty(
    repository: git.Repo, commit_files: Callable, make_files: Callable
):
    make_files(repository, ["test.txt"], "test")
    repository.index.add(["test.txt"])
    repository.git.commit("--allow-empty-message", "-m", "")
    commits: List[git.Commit] = helpers.retrieve_commits(
        repository, "master", reverse=False
    )
    assert squash.get_commit_message(commits[0]) == ""


def test_get_commit_message(repository: git.Repo, commit_files: Callable):
    commit: git.Commit = commit_files(
        repository, ["test.txt"], "content", message="Test"
    )
    assert squash.get_commit_message(commit) == commit.message
