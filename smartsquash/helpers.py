import git
import git.exc
import os
from pathlib import Path
import subprocess
import sys
import collections
import enum
from typing import List, Dict, Set, Optional
from smartsquash.decorators import memorize_files_changed
from loguru import logger


class ErrorMessage(enum.Enum):
    HEAD_DETACHED = "HEAD is detached. Exiting"
    TARGET_EQUALS_CURRENT = "Target branch equals current active branch. Exiting"
    NOT_A_GIT_REPO = "The target is not a git repository. Exiting"
    PATH_NOT_EXIST = "The path doesn't exist. Exiting"
    TARGET_NOT_EXIST = "The target branch doesn't exist. Exiting"

    def __str__(self):
        return self.value


def fatal_log(message: ErrorMessage):
    logger.error(message)
    sys.exit(1)


def get_repo(repo_path: str, target_branch: str) -> git.Repo:
    if not Path(repo_path).exists():
        fatal_log(ErrorMessage.PATH_NOT_EXIST)
    try:
        repo: git.Repo = git.Repo(repo_path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        fatal_log(ErrorMessage.NOT_A_GIT_REPO)
    try:
        repo.heads[target_branch]
    except (git.exc.GitCommandError, git.GitCommandError, AttributeError, IndexError):
        fatal_log(ErrorMessage.TARGET_NOT_EXIST)
    if repo.head.is_detached:
        fatal_log(ErrorMessage.HEAD_DETACHED)
    if repo.active_branch.name == target_branch:
        fatal_log(ErrorMessage.TARGET_EQUALS_CURRENT)
    return repo


def retrieve_commits(
    repo: git.Repo, target_branch: str, reverse: bool = True
) -> List[git.Commit]:
    """
    retrieves commits that are only part of the currently active branch,
    and are not in the target branch
    - git cherry could be used for this, but GitPython doesn't support it
    - Just run raw git command, if this becomes bottleneck
    """
    target_commits_sha: List[git.Commit] = [
        commit.hexsha
        for commit in repo.iter_commits(rev=target_branch)
        if len(commit.parents) < 2  # ignore merge commits
    ]
    commits: List[git.Commit] = [
        commit
        for commit in repo.iter_commits(rev=repo.active_branch)
        if commit.hexsha not in target_commits_sha
        and len(commit.parents) < 2  # ignore merge commits
    ]
    if reverse:
        commits.reverse()
    return commits


@memorize_files_changed
def files_changed_by_commit(working_dir: str, commit: str) -> List[str]:
    output = (
        subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit],
            cwd=working_dir,
        )
        .decode()
        .splitlines()
    )
    return [output for output in output if output]


def get_commits_changed_files(commits: List[git.Commit]) -> Dict[str, Set[str]]:
    commit_changed: Dict[str, Set[str]] = collections.defaultdict(set)
    for commit in commits:
        for file in files_changed_by_commit(commit.repo.working_dir, commit.hexsha):
            commit_changed[commit.hexsha].add(file)
    return commit_changed


def run_rebase(
    repo: git.Repo,
    target_branch: str,
    sequence_editor: str,
    dry: bool = False,
    autosquash: bool = True,
):
    os.environ["GIT_SEQUENCE_EDITOR"] = sequence_editor
    args: List[str] = ["-i", target_branch]
    if autosquash:
        args.insert(0, "--autosquash")
    if dry:
        logger.log("DRY", f"Would run: 'git rebase{' '.join(args)}'")
        sys.exit(0)
    try:
        repo.git.rebase(args)
        print("Rebase done")
    except git.CommandError:
        repo.git.rebase("--abort")
        logger.error("Rebase failed and aborted. You'll need to squash manually")
