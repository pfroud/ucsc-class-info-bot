"""Used to set up reddit api oauth. Also holds some methods for one-time use."""

import praw
import pickle
import os.path

posts_with_comments_pickle_path = os.path.join(os.path.dirname(__file__), 'posts_with_comments.pickle')


def save_posts_with_comments(posts_with_comments):
    """Saves to disk the dict of posts that have already been commented on.

    :param posts_with_comments: dict of posts that already have comments on them
    :type posts_with_comments: dict
    """
    with open(posts_with_comments_pickle_path, 'wb') as file:
        pickle.dump(posts_with_comments, file)
    file.close()


def auth_reddit():
    """Load access information and return PRAW reddit api context.

    :return: praw instance
    :rtype praw.__init__.AuthenticatedReddit
    """
    red = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
                      site_name = 'ucsc_bot')
    with open('access_information.pickle', 'rb') as file:
        access_information = pickle.load(file)
    file.close()
    red.set_access_credentials(**access_information)
    return red


def _get_code(r_):
    """
    Use this first.
    Log into /u/ucsc-class-info-bot then navigate to the url printed.
    """
    url = r_.get_authorize_url('state', 'identity submit edit read', True)
    print(url)


def _save_access_information(r_):
    """
    Use this second.
    Paste the code from the redirect into the function below.
    :param r_: praw instance
    :type r_:
    """
    with open('access_information.pickle', 'wb') as file:
        pickle.dump(r_.get_access_information('code'), file)
    file.close()

# reddit = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
#                      site_name = 'ucsc_bot')

# _get_code()
# _save_access_information()


def load_posts_with_comments():
    """Loads from disk the dict of posts that have already been commented on

    :return: dict of posts that have already been commented on
    :rtype: dict
    """
    if not os.path.isfile(posts_with_comments_pickle_path):
        return dict()

    with open(posts_with_comments_pickle_path, 'rb') as file:
        a_c = pickle.load(file)
    file.close()
    return a_c
