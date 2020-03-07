import argparse
import git
import sys
from pathlib import Path
from smartsquash import sq, helpers
from typing import Dict, Any
from loguru import logger


def get_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target-branch",
        type=str,
        required=False,
        default="master",
        help="Specify branch to target. Default is 'master'",
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=False,
        default=Path.cwd().absolute(),
        help="Specify repo to modify. Uses pwd by default",
    )
    parser.add_argument(
        "--dry", required=False, default=False, action="store_true", help="Run dry"
    )
    parser.add_argument(
        "-s",
        "--squash",
        help="Squash similar commits on your feature branch",
        required=False,
        default=False,
        action="store_true",
    )
    return vars(parser.parse_args())


def setup_logger():
    logger.remove()
    logger.add(sys.stdout, colorize=True, format="<level>{message}</level>")


def main():
    setup_logger()
    args: Dict[str, Any] = get_args()
    repo_path: str = args.get("repo")
    target_branch: str = args.get("target_branch")
    dry: bool = args.get("dry")

    repo: git.Repo = helpers.get_repo(repo_path, target_branch)
    sq.fixup(target_branch, repo, dry)
    if args.get("squash"):
        sq.squash(target_branch, repo, dry)
