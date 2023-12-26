import argparse
import sys
from commands.init import repo_create
from commands.hash import cat_file, hash_object
from commands.log import log_graphviz, log_print
from commands.tree import ls_tree
from repo import repo_find
from object import object_find, object_read

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
        case _:
            print("Bad command.")


if __name__ == "__main__":
    main()
