import argparse
import sys
import os
from commands.init import repo_create
from commands.hash import cat_file, hash_object
from commands.log import log_graphviz, log_print
from commands.tree import ls_tree, tree_checkout
from commands.ref import show_refs
from commands.tag import tag_create
from error import FileSystemException, GitException
from repo import repo_find
from object import object_find, object_read
from ref import ref_list

argparser = argparse.ArgumentParser(description="The stupidest content tracker")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

# pit init
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument(
    "path",
    metavar="directory",
    nargs="?",
    default=".",
    help="Where to create the repository.",
)

# pit cat-file
argsp = argsubparsers.add_parser(
    "cat-file", help="Provide content of repository objects."
)
argsp.add_argument(
    "type",
    metavar="type",
    choices=["blob", "commit", "tag", "tree"],
    help="Specify the type",
)
argsp.add_argument("object", metavar="object", help="The hash of the object to display")

# pit hash-object
argsp = argsubparsers.add_parser(
    "hash-object", help="Compute object ID and optionally creates a blob from a file"
)
argsp.add_argument(
    "-t",
    metavar="type",
    dest="type",
    choices=["blob", "commit", "tag", "tree"],
    default="blob",
    help="Specify the type",
)
argsp.add_argument(
    "-w",
    dest="write",
    action="store_true",
    help="Actually write the object into the database",
)
argsp.add_argument("path", help="Read object from <file>")

# pit log
argsp = argsubparsers.add_parser("log", help="Display history of a given commit.")
argsp.add_argument(
    "-f",
    metavar="format",
    dest="format",
    choices=["print", "graph"],
    default="print",
    help="Specify the log output format",
)
argsp.add_argument("commit", default="HEAD", nargs="?", help="Commit to start at.")

# pit ls-tree
argsp = argsubparsers.add_parser("ls-tree", help="Pretty-print a tree object.")
argsp.add_argument(
    "-r", dest="recursive", action="store_true", help="Recurse into sub-trees"
)
argsp.add_argument("tree", help="A tree-ish object")

# pit checkout
argsp = argsubparsers.add_parser(
    "checkout", help="Checkout a commit inside if a directory"
)
argsp.add_argument("commit", help="The commit of tree to checkout")
argsp.add_argument("path", help="The EMPTY directory to checkout on")

# pit show-refs
argsp = argsubparsers.add_parser("show-refs", help="List references.")

# pit tag
argsp = argsubparsers.add_parser("tag", help="List and create tags.")
argsp.add_argument(
    "-a",
    action="store_true",
    dest="create_tag_object",
    help="Wheter to create a tag object or not",
)
argsp.add_argument("name", nargs="?", help="The new tag's name")
argsp.add_argument(
    "object", default="HEAD", nargs="?", help="The object the new tag will point to"
)
argsp.add_argument("-m", metavar="message", dest="message", help="Tag message")


def cmd_init(args):
    repo_create(args.path)


def cmd_cat_file(args):
    repo = repo_find()
    cat_file(repo, args.object, fmt=args.type.encode())


def cmd_hash_object(args):
    if args.write:
        repo = repo_find()
    else:
        repo = None

    with open(args.path, "rb") as fd:
        sha = hash_object(fd, args.type.encode(), repo)
        print(sha)


def cmd_log(args):
    repo = repo_find()

    match args.format:
        case "print":
            log_print(repo, object_find(repo, args.commit), set())
        case "graph":
            print("digraph pitlog{")
            print("    node[shape=rect]")
            log_graphviz(repo, object_find(repo, args.commit), set())
            print("}")


def cmd_ls_tree(args):
    repo = repo_find()
    ls_tree(repo, args.tree, args.recursive)


def cmd_checkout(args):
    repo = repo_find()
    obj = object_read(repo, object_find(repo, args.commit))

    # If the object is a commit, grab its tree.
    if obj.fmt == b"commit":
        obj = object_read(repo, obj.kvlm[b"tree"].decode("ascii"))

    # Verify that path is an empty directory.
    if os.path.exists(args.path):
        if not os.path.isdir(args.path):
            raise FileSystemException("Not a directory {0}!".format(args.path))
        if os.listdir(args.path):
            raise FileSystemException("Not empty {0}!".format(args.path))
    else:
        os.makedirs(args.path)

    tree_checkout(repo, obj, os.path.realpath(args.path))


def cmd_show_refs(args):
    repo = repo_find()
    refs = ref_list(repo)
    show_refs(repo, refs, prefix="refs")


def cmd_tag(args):
    repo = repo_find()

    if args.name:
        tag_create(
            repo,
            args.name,
            args.object,
            args.message if (args.create_tag_object and args.message) else None,
            type == "object" if args.create_tag_object else "ref",
        )
    else:
        refs = ref_list(repo)
        show_refs(repo, refs["tags"], with_hash=False)


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "init":
            cmd_init(args)
        case "cat-file":
            cmd_cat_file(args)
        case "hash-object":
            cmd_hash_object(args)
        case "log":
            cmd_log(args)
        case "ls-tree":
            cmd_ls_tree(args)
        case "checkout":
            cmd_checkout(args)
        case "show-refs":
            cmd_show_refs(args)
        case "tag":
            cmd_tag(args)
        case _:
            print("Bad command.")


if __name__ == "__main__":
    main()
