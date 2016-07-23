"""Deletes a comment ONLY FROM the pickle of posts with comments. DOES NOT delete comment from reddit.com."""

# You might need to move this to the project's root folder for it to work.

import sys
import tools

if len(sys.argv) != 2:
    print("usage: delete_post_with_comment.py post_id")
    exit(1)

post_id = sys.argv[1]
posts_with_comments = tools.load_posts_with_comments()

pwc_obj = posts_with_comments.get(post_id, None)
if pwc_obj is None:
    print("Key \"{}\" not found.".format(post_id))
    exit(1)

print(pwc_obj)
if input("Delete this? ") == "y":
    del posts_with_comments[post_id]
    tools.save_posts_with_comments(posts_with_comments)
    print("Deleted.")
else:
    print("Not deleted.")
