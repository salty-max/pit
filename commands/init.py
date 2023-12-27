import os
import configparser
import subprocess
from repo import repo_file, repo_dir, GitRepository
from error import FileSystemException, GitException
from util import get_default_branch_name


def repo_create(path):
    """Create a new repository at path."""

    repo = GitRepository(path, True)

    # First, make sure the path either doesn't exist
    # or is an empty dir.

    try:
        if os.path.exists(repo.worktree):
            if not os.path.isdir(repo.worktree):
                raise FileSystemException("%s is not a directory!" % path)
            if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
                raise FileSystemException("%s is not empty!" % path)
        else:
            os.makedirs(repo.worktree)
    except Exception as e:
        print(e)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write(
            "Unnamed repository: edit this file 'description' to name the repository.\n"
        )

    default_branch_name = get_default_branch_name()

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write(f"ref: refs/heads/{default_branch_name}\n")

    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret
