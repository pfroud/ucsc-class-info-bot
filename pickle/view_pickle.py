"""
Lets you view the pickles of found mentions or existing comments.
Use argument 'm' to view found mentions, argument 'p' to view posts with comments.
"""

# You might need to move this to the project's root folder for it to work.

import sys
import tools
from db_core import CourseDatabase, Department, Course  # need this to de-pickle course_database.pickle
from mention_search_posts import PostWithMentions  # need this to de-pickle found_mentions.pickle
from tools import ExistingComment  # need to de-pickle

if len(sys.argv) != 2:
    sys.stderr.write("Usage: view_pickle m|p")
    exit(1)

arg = sys.argv[1]


def print_posts_with_comments(existing_posts_with_comments):
    """Prints the dist of posts which already have comments from the bot.

    :param existing_posts_with_comments: the dict mapping post IDs to ExistingComment objects.
    :type existing_posts_with_comments: dict of <string, ExistingComment>
    """
    for post_id, e_c_obj in sorted(existing_posts_with_comments.items()):
        print("in post " + post_id + ": " + str(e_c_obj))


def print_found_mentions(found_mentions):
    """Prints the list of found mentions.

    :param found_mentions: list of PostWithMentions objects
    """
    for pwm_obj in found_mentions:
        print(pwm_obj)


if 'm' in arg:  # mentions found
    print("Mentions found:")
    print_found_mentions(tools.load_found_mentions())

if 'p' in arg:  # posts with comments
    print("Posts with comments:")
    print_posts_with_comments(tools.load_posts_with_comments())
