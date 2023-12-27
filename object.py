import os
import zlib
import sys
import hashlib
import re
from repo import repo_file, repo_dir
from kvlm import kvlm_parse, kvlm_serialize
from tree import tree_parse, tree_serialize
from ref import ref_resolve
from error import GitException


class GitObject(object):
    """A base git object"""

    def __init__(self, data=None):
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo):
        """
        This function must be implemented by subclasses.

        It must read the object's contents from self.data, a byte string, and do
        whatever it takes to convert it into a meaningful representation. What exactly
        that means depends on the subclass.
        """

        raise Exception("Unimplemented!")

    def deserialize(self, data):
        raise Exception("Unimplemented!")

    def init(self):
        pass  # Just do nothing.


class GitBlob(GitObject):
    fmt = b"blob"

    def serialize(self):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data


class GitCommit(GitObject):
    fmt = b"commit"

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)

    def init(self):
        self.kvlm = dict()


class GitTag(GitCommit):
    fmt = b"tag"


class GitTree(GitObject):
    fmt = b"tree"

    def deserialize(self, data):
        self.items = tree_parse(data)

    def serialize(self):
        return tree_serialize(self)

    def init(self):
        self.items = list()


def object_resolve(repo, name):
    """
    Resolve name to an object hash in repo.

    This function is aware of:
        - short and long hashes
        - tags
        - branches
        - remote branches
    """
    candidates = list()
    hashRE = re.compile(r"^[0-9A-Fa-f]{4,40}$")

    # Empty string? Abort.
    if not name.strip():
        return None

    # HEAD id nonambiguous.
    if name == "HEAD":
        return [ref_resolve(repo, "HEAD")]

    # If it is a hex string, try for a hash.
    if hashRE.match(name):
        # This may be a hash, either small or full. 4 seems to be the
        # minimal length for git to consider something a short hash.
        # This limit is documented in git-rev-parse.
        name = name.lower()
        prefix = name[0:2]

        path = repo_dir(repo, "objects", prefix, mkdir=False)
        if path:
            rem = name[2:]
            for f in os.listdir(path):
                if f.startswith(rem):
                    # Notice a string startswith() itself, so this
                    # works fo full hashes.
                    candidates.append(prefix + f)

    # Try for references.
    as_tag = ref_resolve(repo, "refs/tags/" + name)
    if as_tag:
        candidates.append(as_tag)

    as_branch = ref_resolve(repo, "refs/heads/" + name)
    if as_branch:
        candidates.append(as_branch)

    return candidates


def object_find(repo, name, fmt=None, follow=True):
    """
    Find an git object from various means:
    - full hash
    - short hash
    - tags
    """
    sha = object_resolve(repo, name)
    if not sha:
        raise GitException("No such reference {0}.".format(name))
    if len(sha) > 1:
        raise GitException(
            "Ambiguous reference {0}: Candidates are:\n - {1}".format(
                name, "\n - ".join(sha)
            )
        )

    sha = sha[0]

    if not fmt:
        return sha

    while True:
        obj = object_read(repo, sha)
        #     ^^^^^^^^^^^ < this is a bit agressive: we're reading
        # the full object just to get its type. And we're doing
        # that in a loop, albeit normally short. Not very efficient
        # performance wise.

        if obj.fmt == fmt:
            return sha

        if not follow:
            return None

        # Follow tags
        if obj.fmt == b"tag":
            sha = obj.kvlm[b"object"].decode("ascii")
        elif obj.fmt == b"commit" and fmt == b"tree":
            sha = obj.kvlm[b"tree"].decode("ascii")
        else:
            return None


def object_read(repo, sha):
    """
    Read object sha from Git repository repo. Return a
    GitObject whose exact type depends on the object.
    """

    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    if not os.path.isfile(path):
        return None

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # Read object type
        x = raw.find(b" ")
        fmt = raw[0:x]

        # Read and validate object size
        y = raw.find(b"\x00", x)
        size = int(raw[x:y].decode("ascii"))
        if size != len(raw) - y - 1:
            raise GitException(f"Malformed object {sha}: bad length")

        # Pick constructor
        match fmt:
            case b"commit":
                c = GitCommit
            case b"tree":
                c = GitTree
            case b"tag":
                c = GitTag
            case b"blob":
                c = GitBlob
            case _:
                raise GitException(
                    "Unknown type {0} for object {1}".format(fmt.decode("ascii"), sha)
                )

        # Call constructor and return object
        return c(raw[y + 1 :])


def object_write(obj, repo=None):
    """
    Create sha based on an object.
    """

    # Serialize object data
    data = obj.serialize()
    # Add header
    result = obj.fmt + b" " + str(len(data)).encode() + b"\x00" + data
    # Compute hash
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        # Compute path
        path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, "wb") as f:
                # Compress and write
                f.write(zlib.compress(result))

    return sha
