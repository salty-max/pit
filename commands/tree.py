import os
from object import object_find, object_read


def ls_tree(repo, ref, recursive=None, prefix=""):
    sha = object_find(repo, ref, fmt=b"tree")
    obj = object_read(repo, sha)

    for item in obj.items:
        if len(item.mode) == 5:
            type = item.mode[0:1]
        else:
            type = item.mode[0:2]

        match type:  # Determine the type.
            case b"04":
                type = "tree"
            case b"10":
                type = "blob"  # A regular file.
            case b"12":
                type = "blob"  # A symlink. Blob contents is link target.
            case b"16":
                type = "commit"  # A submodule
            case _:
                raise GitException("Weird tree leaf mode {}".format(item.mode))

        if not (recursive and type == "tree"):  # This is a leaf.
            print(
                "{0} {1} {2}\t{3}".format(
                    "0" * (6 - len(item.mode)) + item.mode.decode("ascii"),
                    # Git's ls-tree displays the type of the object pointed to.
                    type,
                    item.sha,
                    os.path.join(prefix, item.path),
                )
            )
        else:  # This is a branch, recurse.
            ls_tree(repo, item.sha, recursive, os.path.join(prefix, item.path))