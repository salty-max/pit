from object import object_read
from datetime import datetime, timedelta


def log_print(repo, sha, seen):
    """
    Pretty-print a commit's  history
    """
    if sha in seen:
        return
    seen.add(sha)

    commit = object_read(repo, sha)
    short_hash = sha[0:8]
    message = commit.kvlm[None].decode("utf8").strip()
    message = message.replace("\\", "\\\\")
    message = message.replace('"', '\\"')

    author_date = commit.kvlm[b"author"].decode("utf8").strip()

    x = author_date.find(">")
    y = author_date.find("+")

    author = author_date[: x + 1]
    timestamp = int(author_date[x + 1 : y - 1])
    offset = author_date[y:]
    date = date_utc(timestamp, offset)

    if "\n" in message:  # Keep only the first line.
        message = message[: message.index("\n")]

    # Print the commit SHA.
    print("\x1b[0;33mcommit %s\x1b[0m" % sha)
    # Print the commit's author.
    print("Author: %s" % author)
    # Print the commit's date.
    print("Date: %s\n" % date)

    print('    "%s"\n' % message)
    assert commit.fmt == b"commit"

    if not b"parent" in commit.kvlm.keys():
        # Base case: the initial commit.
        return

    parents = commit.kvlm[b"parent"]

    if type(parents) != list:
        parents = [parents]

    for p in parents:
        p = p.decode("ascii")
        print("commit {0} -> commit {1}\n".format(sha[0:8], p[0:8]))
        log_print(repo, p, seen)


def log_graphviz(repo, sha, seen):
    """
    Return a commit's history in dot format
    """
    if sha in seen:
        return
    seen.add(sha)

    commit = object_read(repo, sha)
    short_hash = sha[0:8]
    message = commit.kvlm[None].decode("utf8").strip()
    message = message.replace("\\", "\\\\")
    message = message.replace('"', '\\"')

    if "\n" in message:  # Keep only the first line
        message = message[: message.index("\n")]

    print('    c_{0} [label="{1}: {2}"]'.format(sha, short_hash, message))
    assert commit.fmt == b"commit"

    if not b"parent" in commit.kvlm.keys():
        # Base case: the initial commit
        return

    parents = commit.kvlm[b"parent"]

    if type(parents) != list:
        parents = [parents]

    for p in parents:
        p = p.decode("ascii")
        print("    c_{0} -> c_{1};".format(sha, p))
        log_graphviz(repo, p, seen)


def date_utc(timestamp, offset):
    date = datetime.utcfromtimestamp(timestamp)
    offset_hours = int(offset[:-2])
    offset_minutes = int(offset[-2:])
    offset_delta = timedelta(hours=offset_hours, minutes=offset_minutes)
    date += offset_delta

    return date
