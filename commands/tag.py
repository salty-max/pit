import collections
from object import object_find, object_write, GitTag
from util import get_user_name_email
from ref import ref_create


def tag_create(repo, name, ref, message=None, create_tag_object=False):
    # Get the GitObject from the object reference
    sha = object_find(repo, ref)

    if create_tag_object:
        tag = GitTag()

        tag.kvlm = collections.OrderedDict()
        tag.kvlm[b"object"] = sha.encode()
        tag.kvlm[b"type"] = b"commit"
        tag.kvlm[b"tag"] = name.encode()

        user_info = get_user_name_email()
        tag.kvlm[b"tagger"] = user_info.encode()

        tag.kvlm[None] = message.encode() if message != None else b""

        tag_sha = object_write(tag)

        # Create reference
        ref_create(repo, "tags/" + name, tag_sha)
    else:
        # Create lightweight tag (ref)
        ref_create(repo, "tags/" + name, sha)
