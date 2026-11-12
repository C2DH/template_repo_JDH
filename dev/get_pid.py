import re
import subprocess
from pathlib import Path


def get_pid_from_repo(repo_dir: Path | None = None) -> str:
    """Infer the article pid from the current git repository.

    JDH article repos are named exactly after the article's pid, e.g.
    https://github.com/jdh-observer/7XSDVCtnbXva -> pid "7XSDVCtnbXva".
    """
    repo_dir = repo_dir or Path(__file__).resolve().parent

    try:
        remote_url = subprocess.check_output(
            ["git", "-C", str(repo_dir), "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        # Matches git@github.com:org/repo.git or https://github.com/org/repo(.git)
        match = re.search(r"[:/]([^/]+?)(\.git)?/?$", remote_url)
        if match:
            return match.group(1)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback: assume the folder is named after the pid (as in this repo).
    return repo_dir.name
