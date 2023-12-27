import os
import collections
from repo import repo_dir, repo_file


def ref_resolve(repo, ref):
    path = repo_file(repo, ref)

    # Sometimes, an indirect reference may be broken. This is normal
    # in one specific case: we're looking for HEAD on a new repository
    # with no commits. In that case, .git/HEAD points to "ref:
    # refs/heads/main", but ./git/refs/heads/main doesn't exist yet
    # (since there's no commit for it to refer to).
    if not os.path.isfile(path):
        return None

    with open(path, "r") as fp:
        data = fp.read()[:-1]
        # Drop final \n

    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    else:
        return data


def ref_list(repo, path=None):
    if not path:
        path = repo_dir(repo, "refs")

    ret = collections.OrderedDict()
    # Git shows refs sorted. To do the same, we use
    # an OrderedDict and sort the output of listdir
    for f in sorted(os.listdir(path)):
        can = os.path.join(path, f)
        if os.path.isdir(can):
            ret[f] = ref_list(repo, can)
        else:
            ret[f] = ref_resolve(repo, can)

    return ret


def ref_create(repo, ref_name, sha):
    with open(repo_file(repo, "refs/" + ref_name), "w") as fp:
        fp.write(sha + "\n")
