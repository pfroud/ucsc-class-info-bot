"""
Scrapes posts on /r/UCSC for mentions of courses.
"""

import re
import praw
import tools
from tools import trunc_pad
import mention_parse


class PostWithMentions:
    """Info about a specefic post and mentions found in that post."""

    def __init__(self, post_id, mentions_list):
        self.post_id = post_id
        self.mentions_list = mentions_list

    def __str__(self):
        return "mentions in post id {}: {}".format(self.post_id, self.mentions_list)


def _get_mentions_in_submission(counter, submission_):
    """Finds mentions of a course in a submission's title, selftext, and comments.

    :param counter: counter to print in table row
    :type counter: int
    :param submission_: a praw submission object
    :type submission_: praw.objects.Submission
    :return: a PostWithMentions object which has the post ID and a list of strings of mentions
    :rtype: PostWithMentions
    """
    mentions_list = []
    mentions_list.extend(_get_mentions_in_string(submission_.title))

    mentions_list.extend(_get_mentions_in_string(submission_.selftext))

    submission_.replace_more_comments(limit = None, threshold = 0)
    flat_comments = praw.helpers.flatten_tree(submission_.comments)
    for comment in flat_comments:
        if comment.author is None or comment.author.name == 'ucsc-class-info-bot':
            continue
        mentions_list.extend(_get_mentions_in_string(comment.body))

    mentions_list = _remove_list_duplicates_preserve_order(mentions_list)

    author = submission_.author
    if author is None:
        author_name = "[deleted]"
    else:
        author_name = author.name

    print('{num}{_}{id}{_}{author}{_}{title}{_}{mentions}'
          .format(num = trunc_pad(str(counter), 'num'),
                  id = trunc_pad(submission_.id, "id"),
                  author = trunc_pad(author_name, "author"),
                  title = trunc_pad(submission_.title, "title"),
                  mentions = mentions_list,
                  _ = '  '))

    if not mentions_list:  # if list is empty
        return None
    else:
        return PostWithMentions(submission_.id, mentions_list)


def _get_mentions_in_string(source_):
    """Finds mentions of courses (department and number) in a string.

    :param source_: string to look for courses in.
    :type source_: str
    :return: list of strings of course names
    :rtype: list
    """

    return mention_parse.parse_string(source_)


def _unify_mention_format(mention_):
    """Gaurentees a space between deptartment and number, removes leading zeroes, and expands CS and CE to CMPS and CMPE.

    :param mention_: the mention to reformat
    :type mention_: str
    :return: the reformatted mention
    :rtype: str
    """
    m = re.match("([a-zA-Z]+ ?)([0-9]+[A-Za-z]?)", mention_)
    dept = m.group(1).lower().strip()
    num = m.group(2).lower().lstrip("0")

    if dept == 'cs':
        dept = 'cmps'

    if dept == 'ce':
        dept = 'cmpe'

    return dept + " " + num


def _remove_list_duplicates_preserve_order(input_list):
    """Removes duplicates from a list, while preserving order.
    To do this easily without preserving order, do list(set(input_list)).

    :param input_list: the list to remove duplicates from, while preserving order
    :type input_list: list
    :return: the list with duplicates removed, with order preserved
    :rtype: list
    """
    new_list = []

    for i in input_list:
        i = _unify_mention_format(i)
        if i not in new_list:
            new_list.append(i)

    return new_list


def find_mentions(reddit, num_posts_, running_on_own = False):
    """Finds and saves to disk course mentions in new posts on /r/UCSC.

    :param running_on_own: whether file is being ran by itself or imported by reddit_bot.py
    :type running_on_own: bool
    :param reddit: authorized reddit praw object
    :type reddit: praw.Reddit
    :param num_posts_:
    :type num_posts_: int
    :return: list of PostWithMentions instances
    :rtype: list
    """

    # use this to find mentions in only one post
    # tools.save_found_mentions([_get_mentions_in_submission(0, reddit.get_submission(submission_id = "4j4i0y"))])
    # return

    print('{num}{_}{id}{_}{author}{_}{title}{_}mentions'
          .format(num = trunc_pad("#", 'num'),
                  id = trunc_pad("id"),
                  author = trunc_pad("author"),
                  title = trunc_pad("title"),
                  _ = '  ').upper())

    subreddit = reddit.get_subreddit('ucsc')
    list_of_posts_with_mentions = []

    for counter, submission in enumerate(subreddit.get_new(limit = num_posts_), start = 1):
        found_mentions = _get_mentions_in_submission(counter, submission)
        if found_mentions is not None:
            list_of_posts_with_mentions.append(found_mentions)

    if running_on_own:
        tools.save_found_mentions(list_of_posts_with_mentions)

    print("------------------------------")
    for post_with_mention in list_of_posts_with_mentions:
        print(str(post_with_mention))

    return list_of_posts_with_mentions


if __name__ == "__main__":
    import sys

    num_posts = 1
    if len(sys.argv) == 2:
        num_posts = int(sys.argv[1])
    find_mentions(tools.auth_reddit(), num_posts, running_on_own = True)
