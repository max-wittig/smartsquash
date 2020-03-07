import git
import sys
from typing import List, Dict, Set, Optional
from smartsquash.helpers import (
    retrieve_commits,
    get_commits_changed_files,
    run_rebase,
)
from smartsquash.fixup import (
    run_fixup,
    get_closest_change_commit,
    get_files_changed_in_staging,
)
from smartsquash.squash import get_rebase_data
from loguru import logger


def squash(target_branch: str, repo: git.Repo, dry: bool = False):
    all_commits: List[git.Commit] = retrieve_commits(repo, target_branch)
    has_rebase, rebase_data = get_rebase_data(all_commits)
    rebase_data: str = rebase_data.replace("'", "", -1)
    if has_rebase:
        run_rebase(
            repo, target_branch, f"echo '{rebase_data}' >", dry, autosquash=False
        )


def fixup(
    target_branch: str, repo: git.Repo, add: bool = False, dry: bool = False
) -> bool:
    if not repo.is_dirty():
        logger.info("Repository is not dirty. No files to fixup.")
        return False
    commits: List[git.Commit] = retrieve_commits(repo, target_branch, reverse=False)
    logger.info("Fetching files changed by commits...")
    commit_changed_files: Dict[str, Set[str]] = get_commits_changed_files(commits)
    files_changed: Set[str] = get_files_changed_in_staging(repo)
    closes_change_commit: Optional[str] = get_closest_change_commit(
        files_changed, commit_changed_files
    )
    if closes_change_commit:
        if dry:
            sys.exit(0)
        run_fixup(repo, target_branch, closes_change_commit, add, dry)
        return True
    logger.error("No commits found to fixup. You'll need to fixup manually")
    return False
