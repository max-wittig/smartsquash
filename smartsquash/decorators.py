import functools
from typing import Callable, Dict, List


def memorize_files_changed(func) -> Callable:
    @functools.wraps(func)
    def wrapper_memorize_paths(*args, **kwargs) -> Dict[str, List[str]]:
        commit_sha: str = args[1]

        if not hasattr(wrapper_memorize_paths, "paths"):
            wrapper_memorize_paths.paths = {}
        if not wrapper_memorize_paths.paths.get(commit_sha):
            wrapper_memorize_paths.paths[commit_sha] = func(*args, **kwargs)
        return wrapper_memorize_paths.paths[commit_sha]

    return wrapper_memorize_paths
