"""Used to set up reddit api oauth."""

import pickle
import praw


def auth_reddit():
    """Load access information and return PRAW reddit api context.

    :return: praw instance
    :rtype praw.__init__.AuthenticatedReddit
    """
    red = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
                      site_name = 'ucsc_bot')
    with open('pickle/access_information.pickle', 'rb') as file:
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
    with open('pickle/access_information.pickle', 'wb') as file:
        pickle.dump(r_.get_access_information('code'), file)
    file.close()

# reddit = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
#                      site_name = 'ucsc_bot')

# _get_code()
# _save_access_information()
