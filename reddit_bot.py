"""
Runs find_mentions and post_comments.
"""

from db_core import CourseDatabase, Department, Course  # need this to de-pickle course_database.pickle
from mention_search_posts import find_mentions
from post_comments import post_comments
import tools
import sys

num_posts = 10
if len(sys.argv) == 2:
    num_posts = int(sys.argv[1])

reddit = tools.auth_reddit()
post_comments(find_mentions(reddit, num_posts), reddit)
