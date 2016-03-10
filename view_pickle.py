"""
Lets you view the pickles of found mentions or existing comments.
"""

import sys
import tools
from db_core import CourseDatabase, Department, Course  # need this to de-pickle course_database.pickle
from mention_search_posts import PostWithMentions  # need this to de-pickle found_mentions.pickle
from tools import ExistingComment  # need to de-pickle


if len(sys.argv) != 2:
    sys.stderr.write("Usage: view_pickle m|p")
    exit(1)

arg = sys.argv[1]

if 'm' in arg:  # mentions found
    print("Mentions found:")
    tools.print_found_mentions(tools.load_found_mentions())

if 'p' in arg:  # posts with comments
    print("Posts with comments:")
    tools.print_posts_with_comments(tools.load_posts_with_comments())
