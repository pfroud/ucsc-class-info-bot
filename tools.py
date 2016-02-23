"""Functions to do reddit authentication, file saving and loading, and data structure printing,
and varialbes used by multiple files."""

import pickle
import praw
import os
import warnings

# use this to set up PRAW for the first time
# reddit = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
#                      site_name = 'ucsc_bot')

# _get_code()
# _save_access_information()

# widths of column for printing tables to console. used by trunc_pad()
_column_widths = {"id": 7,
                  "author": 11,
                  "title": 30,
                  "action": 17}


class ExistingComment:
    """Info about an existing comment with class info."""

    def __init__(self, comment_id_, mentions_):
        self.comment_id = comment_id_
        self.mentions_list = mentions_

    def __str__(self):
        return "existing comment: {} -> {}".format(self.comment_id, self.mentions_list)


def trunc_pad(string_, use_ = None):
    """Truncates and pads with spaces string_ to be printed in a table.
    The padding width is indicated by use_.

    :param string_: string to be truncated and padded
    :type string_: str
    :param use_: string identifying which column the string is in.
    :type use_: str
    :return: the input string, truncated and padded
    :rtype: str
    """
    if use_ is None:
        use_ = string_
    width = _column_widths[use_]
    return string_[:width].ljust(width)


def auth_reddit():
    """Loads access information and returns PRAW reddit api context.

    :return: praw instance
    :rtype praw.__init__.AuthenticatedReddit
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        red = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
                          site_name = 'ucsc_bot')

    with open('pickle/access_information.pickle', 'rb') as file:
        access_information = pickle.load(file)
    file.close()
    red.set_access_credentials(**access_information)
    return red


def _get_code(r_):
    """
    Use this for first-time PRAW setup. Use this first.
    Log into /u/ucsc-class-info-bot then navigate to the url printed.
    """
    url = r_.get_authorize_url('state', 'identity submit edit read', True)
    print(url)


def _save_access_information(r_):
    """
    Use this for first-time PRAW setup. Use this second.
    Paste the code from the redirect into the function below.
    :param r_: praw instance
    :type r_:
    """
    with open('pickle/access_information.pickle', 'wb') as file:
        pickle.dump(r_.get_access_information('code'), file)
    file.close()


def print_posts_with_comments(existing_posts_with_comments):
    """Prints the dist of posts which already have comments from the bot.

    :param existing_posts_with_comments: the dict mapping post IDs to ExistingComment objects.
    :type existing_posts_with_comments: dict of <string, ExistingComment>
    """
    for post_id, e_c_obj in existing_posts_with_comments.items():
        print("in post " + post_id + ": " + str(e_c_obj))


def print_found_mentions(found_mentions):
    """Prints the list of found mentions.

    :param found_mentions: list of PostWithMentions objects
    """
    for pwm_obj in found_mentions:
        print(pwm_obj)


def load_posts_with_comments():
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


def load_found_mentions():
    """Loads from disk the list of found mentions from the last run of find_mentions().

    :return: list of PostWithMentions objects
    :rtype: list
    """
    with open("pickle/found_mentions.pickle", 'rb') as file:
        mentions = pickle.load(file)
    file.close()
    return mentions


def save_found_mentions(found_mentions):
    """Saves to disk mentions found from from the last run of find_mentions().
    This is used in both post_comments.py and in find_mentions.py so I have put it in tools.py.

    :param found_mentions: list of PostWithMentions objects
    :type found_mentions: list
    """
    with open("pickle/found_mentions.pickle", 'wb') as file:
        pickle.dump(found_mentions, file)
    file.close()
