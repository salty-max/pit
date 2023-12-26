import sys
from object import object_read, object_find, object_write, GitBlob
from error import GitException


def cat_file(repo, obj, fmt=None):
    """
    Print out the content of a git object.
    """
    obj = object_read(repo, object_find(repo, obj, fmt=fmt))

    sys.stdout.buffer.write(obj.serialize())


def hash_object(fd, fmt, repo=None):
    """
    Hash object, writing it to repo if provided.
    """
    data = fd.read()

    # Choose constructor according to fmt argument
    match fmt:
        case b"commit":
            obj = GitCommit(data)
        case b"tree":
            obj = GitTree(data)
        case b"tag":
            obj = GitTag(data)
        case b"blob":
            obj = GitBlob(data)
        case _:
            raise GitException("Unknown type %s!" % fmt)

    return object_write(obj, repo)
