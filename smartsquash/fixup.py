import git.exc
from smartsquash.helpers import run_rebase
from typing import Dict, Set, Optional


def get_files_changed_in_staging(repo: git.Repo) -> Set[str]:
    output: Set[str] = (repo.git.diff("--name-only", "--cached", "-r").splitlines())
    return set(output)


def get_closest_change_commit(
    files_changed: Set[str], commit_changed_files: Dict[str, Set[str]]
) -> Optional[str]:
    for commit_sha, files in commit_changed_files.items():
        if files_changed.issubset(files):
            return commit_sha
    return None


def run_fixup(
    repo: git.Repo, target_branch: str, fixup_commit_sha: str, add: bool, dry: bool
):
    command = ["--fixup", fixup_commit_sha]
    if add:
        command.insert(0, "-a")
    repo.git.commit(*command)
    run_rebase(repo, target_branch, "true", dry, autosquash=True)
