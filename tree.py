class GitTreeLeaf(object):
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.sha = sha
        self.path = path


def tree_parse_one(raw, start=0):
    # Find the space terminator of the mode.
    x = raw.find(b" ", start)
    assert x - start == 5 or x - start == 6

    # Read the mode.
    mode = raw[start:x]
    if len(mode) == 5:
        # Normalize the six bytes.
        mode = b" " + mode

    # Find the null terminator of the path
    y = raw.find(b"\x00", x)
    # and read the path
    path = raw[x + 1 : y]

    # Read the SHA and convert to a hex string.
    sha = format(int.from_bytes(raw[y + 1 : y + 21], "big"), "040x")
    return y + 21, GitTreeLeaf(mode, path.decode("utf8"), sha)


def tree_parse(raw):
    pos = 0
    max = len(raw)
    ret = list()

    while pos < max:
        pos, data = tree_parse_one(raw, pos)
        ret.append(data)

    return ret


def tree_leaf_sort_key(leaf):
    if leaf.mode.startwith(b"10"):
        return leaf.path
    else:
        return leaf.path + "/"


def tree_serialize(obj):
    obj.items.sort(key=tree_leaf_sort_key)
    ret = b""

    for i in obj.items:
        ret += i.mode
        ret += b" "
        ret += i.path.encode("utf8")
        ret += b"\x00"
        sha = int(i.sha, 16)
        ret += sha.to_bytes(20, byteorder="big")

    return ret
