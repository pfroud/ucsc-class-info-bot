"""Functions to do reddit authentication, file saving and loading, and data structure printing,
and varialbes used by multiple files."""

import pickle
import praw
import os
import warnings


# use this to set up PRAW for the first time:
# reddit = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v1.0 (by /u/ucsc-class-info-bot)',
#                      site_name = 'ucsc_bot')

# _get_code()
# _save_access_information()

def _get_code(r_):
    """
    Use this for first-time PRAW setup. Use this then _save_access_information().
    Log into /u/ucsc-class-info-bot then navigate to the url printed.
    From http://praw.readthedocs.io/en/v3.6.0/pages/oauth.html
    """
    url = r_.get_authorize_url('state', 'identity submit edit read', True)
    print(url)


def _save_access_information(r_) -> None:
    """
    Use this for first-time PRAW setup.
    Paste the code from the redirect into the function below.
    From http://praw.readthedocs.io/en/v3.6.0/pages/oauth.html
    :param r_: praw instance
    :type r_: praw.Reddit
    """
    with open('pickle/access_information.pickle', 'wb') as file:
        pickle.dump(r_.get_access_information('code'), file)
    file.close()


class ExistingComment:
    """Info about an existing comment with class info."""

    def __init__(self, comment_id_: str, mentions_: list):
        self.comment_id = comment_id_
        self.mentions_list = mentions_

    def __str__(self):
        return "existing comment: {} -> {}".format(self.comment_id, self.mentions_list)


# widths of column for printing tables to console.
_column_widths = {'num': 2,
                  "id": 7,
                  "author": 15,
                  "title": 35,
                  "action": 17}


def trunc_pad(string_: str, column_name: str = None) -> str:
    """Truncates and pads with spaces string_ to be printed in a table.
    The padding widths are given in the dict _column_widths.
    If column_name isn't specifeid, the string is used as the column name.

    :param string_: string to be truncated and padded
    :type string_: str
    :param column_name: string identifying which column the string is in.
    :type column_name: str
    :return: the input string, truncated and padded
    :rtype: str
    """
    if column_name is None:
        column_name = string_

    width = _column_widths[column_name]
    if len(string_) > width:
        return string_[:width - 3] + '...'
    else:
        return string_.ljust(width)


def auth_reddit() -> praw.Reddit:
    """Loads access information and returns PRAW reddit api context.

    :return: praw instance
    :rtype praw.Reddit
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # suppress PRAW warning about user agent containing 'bot'
        red = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
                          site_name = 'ucsc_bot')

    with open('pickle/access_information.pickle', 'rb') as file:
        access_information = pickle.load(file)
    file.close()
    red.set_access_credentials(**access_information)
    return red


def load_posts_with_comments() -> dict:
    """Loads from disk the dict of posts that have already been commented on.

    :return: dict of <string,ExistingComment> of posts that have already been commented on
    :rtype: dict
    """
    if not os.path.isfile("pickle/posts_with_comments.pickle"):
        return dict()

    with open("pickle/posts_with_comments.pickle", 'rb') as file:
        a_c = pickle.load(file)
    file.close()
    return a_c


def save_posts_with_comments(posts_with_comments: dict) -> None:
    """Saves to disk the dict of posts that have already been commented on.

    :param posts_with_comments:  dict of <string,ExistingComment> of posts that already have comments on them
    :type posts_with_comments: dict
    """
    with open("pickle/posts_with_comments.pickle", 'wb') as file:
        pickle.dump(posts_with_comments, file)
    file.close()


def load_found_mentions() -> list:
    """Loads from disk the list of found mentions from the last run of find_mentions().

    :return: list of PostWithMentions objects
    :rtype: list
    """
    with open("pickle/found_mentions.pickle", 'rb') as file:
        mentions = pickle.load(file)
    file.close()
    return mentions


def save_found_mentions(found_mentions: list) -> None:
    """Saves to disk mentions found from from the last run of find_mentions().
    This is used in both post_comments.py and in mention_search_posts.py so I have put it in tools.py.

    :param found_mentions: list of PostWithMentions objects
    :type found_mentions: list
    """
    with open("pickle/found_mentions.pickle", 'wb') as file:
        pickle.dump(found_mentions, file)
    file.close()
