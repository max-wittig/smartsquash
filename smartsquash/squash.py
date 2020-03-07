import git
import git.exc
import itertools
import subprocess
import collections
from typing import List, Tuple, Dict, Set
from smartsquash import helpers
from loguru import logger


def get_commits_in_between(
    commit_a: git.Commit, commit_b: git.Commit, commits: List[git.Commit]
) -> List[git.Commit]:
    """Returns commits from """
    find_a_index = -1
    find_b_index = -1
    for index, commit in enumerate(commits):
        if commit_a.hexsha == commit.hexsha:
            find_a_index = index
        if commit_b.hexsha == commit.hexsha:
            find_b_index = index
        if find_a_index != -1 and find_b_index != -1:
            break
    first: int = find_a_index if find_a_index < find_b_index else find_b_index
    second: int = find_b_index if first == find_a_index else find_a_index
    return commits[first + 1 : second]


def has_relevant_files_changed_in_between(
    commit_a: git.Commit,
    commit_b: git.Commit,
    commits: List[git.Commit],
    commit_changed_files: Dict[str, Set[str]],
) -> bool:
    """
    we should look for other files that changed in between commits AND
    in addition also change 'our files'(the files from 'commit_a,commit_b')

    We don't care about other files that may have changed in between
    """
    commits_in_between = get_commits_in_between(commit_a, commit_b, commits)
    files = commit_changed_files[commit_a.hexsha]
    for commit in commits_in_between:
        for file in commit_changed_files[commit.hexsha]:
            if file in files and commit_changed_files[commit.hexsha] != files:
                return True
    return False


def commit_diff_empty(commit_a: git.Commit, commit_b: git.Commit) -> bool:
    output = subprocess.check_output(
        ["git", "diff", f"{commit_a.hexsha}...{commit_b.hexsha}"],
        cwd=commit_a.repo.working_dir,
    ).decode()
    return not output


def has_same_files(files_a: List[str], files_b: List[str]) -> bool:
    files_a: List[str] = sorted(files_a)
    files_b: List[str] = sorted(files_b)
    return files_a == files_b


def get_commit_message(commit: git.Commit) -> str:
    if commit.message:
        return commit.message.split("\n")[0]
    return ""


def fulfils_conditions(
    commit_a: git.Commit,
    commit_b: git.Commit,
    commits: List[git.Commit],
    commit_changed_files: Dict[str, Set[str]],
) -> bool:
    if not has_same_files(
        list(commit_changed_files[commit_a.hexsha]),
        list(commit_changed_files[commit_b.hexsha]),
    ):
        return False

    if has_relevant_files_changed_in_between(
        commit_a, commit_b, commits, commit_changed_files
    ):
        return False
    if commit_diff_empty(commit_a, commit_b):
        return False
    return True


def get_squash_combinations(
    commits: List[git.Commit], commit_changed_files: Dict[str, Set[str]]
):
    squash_combinations: Dict[str, List[git.Commit]] = collections.defaultdict(list)
    for commit_a, commit_b in itertools.combinations(commits, 2):
        if not fulfils_conditions(commit_a, commit_b, commits, commit_changed_files):
            continue
        squash_combinations[commit_a.hexsha].append(commit_b)
    return squash_combinations


def get_rebase_data(commits: List[git.Commit]) -> Tuple[bool, str]:
    has_rebase = False
    data = ""
    logger.info("Fetching files changed by commits...")
    commit_changed_files: Dict[str, Set[str]] = helpers.get_commits_changed_files(
        commits
    )
    logger.info(f"Comparing {len(commits)} commits with each other...")
    squash_combinations: Dict[str, List[git.Commit]] = get_squash_combinations(
        commits, commit_changed_files
    )

    squash_list: List[str] = []
    for commit in commits:
        if commit.hexsha in squash_list:
            continue
        if to_squash_commits := squash_combinations.get(commit.hexsha):
            # commit has commits to be squashed
            data += f"pick {commit.hexsha[:7]} {get_commit_message(commit)}\n"
            for to_squash in to_squash_commits:
                has_rebase = True
                data += (
                    f"fixup {to_squash.hexsha[:7]} {get_commit_message(to_squash)}\n"
                )
                squash_list.append(to_squash.hexsha)
        else:
            data += f"pick {commit.hexsha[:7]} {get_commit_message(commit)}\n"
    return has_rebase, data
