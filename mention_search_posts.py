"""
Scrapes posts on /r/UCSC for mentions of courses.
"""

from typing import Optional, List
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


def _get_mentions_in_submission(counter: int, submission_: praw.objects.Submission) -> Optional[PostWithMentions]:
    """Finds mentions of a course in a submission's title, selftext, and comments.

    :param counter: counter to print in table row
    :type counter: int
    :param submission_: a praw submission object
    :type submission_: praw.objects.Submission
    :return: a PostWithMentions object which has the post ID and a list of strings of mentions
    :rtype: PostWithMentions, None
    """
    mentions_list = []
    mentions_list.extend(_get_mentions_in_string(submission_.title))
    mentions_list.extend(_get_mentions_in_string(submission_.selftext))

    submission_.replace_more_comments(limit = None, threshold = 0)
    flat_comments = praw.helpers.flatten_tree(submission_.comments)

    # TODO replace look-before-you-leap with try/except
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

    if not mentions_list:
        return None
    else:
        return PostWithMentions(submission_.id, mentions_list)


def _get_mentions_in_string(source: str) -> List[str]:
    """Finds mentions of courses (department and number) in a string. (Just calls a function in mentions_parse.py.)

    :param source: string to look for courses in.
    :type source: str
    :return: list of strings of course names
    :rtype: list
    """

    return mention_parse.parse_string(source)


def _unify_mention_format(mention: str) -> str:
    """Gaurentees a space between deptartment and number, removes leading zeroes, and expands CS and CE to CMPS and CMPE.

    :param mention: the mention to reformat
    :type mention: str
    :return: the reformatted mention
    :rtype: str
    """
    matches = re.match("([a-zA-Z]+ ?)([0-9]+[A-Za-z]?)", mention)
    dept = matches.group(1).lower().strip()
    num = matches.group(2).lower().lstrip("0")

    if dept == 'cs':
        dept = 'cmps'

    if dept == 'ce':
        dept = 'cmpe'

    return dept + " " + num


def _remove_list_duplicates_preserve_order(input_list: List[str]) -> List[str]:
    """Removes duplicates from a list, while preserving order.
    There's no built-in way to do this and a lot of weird ways to do it on Stack Overflow.
    I just used this one http://stackoverflow.com/a/6764969

    To do this easily without preserving order, do list(set(input_list)).

    :param input_list: the list to remove duplicates from, while preserving order
    :type input_list: list
    :return: the list with duplicates removed, with order preserved
    :rtype: list
    """
    uniques = []

    for element in input_list:
        element = _unify_mention_format(element)
        if element not in uniques:
            uniques.append(element)

    return uniques


def find_mentions(reddit: praw.Reddit, num_posts: int) -> List[PostWithMentions]:
    """Finds and saves to disk course mentions in new posts on /r/UCSC.

    :param reddit: authorized reddit praw object
    :type reddit: praw.Reddit
    :param num_posts: the number of posts to look in.
    :type num_posts: int
    :return: list of PostWithMentions instances
    :rtype: list
    """

    # use this to find mentions in only one post:
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

    for counter, submission in enumerate(subreddit.get_new(limit = num_posts), start = 1):
        found_mentions = _get_mentions_in_submission(counter, submission)
        # TODO replace look-before-you-leap with try/except
        if found_mentions is not None:
            list_of_posts_with_mentions.append(found_mentions)

    if __name__ == "__main__":
        tools.save_found_mentions(list_of_posts_with_mentions)

    print("------------------------------")
    for post_with_mention in list_of_posts_with_mentions:
        print(str(post_with_mention))

    return list_of_posts_with_mentions


def main():
    """Searches posts for mentions."""
    if __name__ == "__main__":
        import sys

        num_posts = 1
        if len(sys.argv) == 2:
            num_posts = int(sys.argv[1])
        find_mentions(tools.auth_reddit(), num_posts)

main()
