"""Used to set up reddit api oauth. Also holds some methods for one-time use."""

import praw
import pickle
import os.path

posts_with_comments_pickle_path = os.path.join(os.path.dirname(__file__), 'pickle/posts_with_comments.pickle')


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


def print_csv_row(submission_, action, mentions_current, mentions_previous):
    """Prints a CSV row to stdout to be used as a log about what happened with a comment.

    :param submission_: Submission object that you are commenting on
    :type submission_:  praw.objects.Submission
    :param action: string describing the action taken
    :type action: str
    :param mentions_current: list of current class mentions
    :type mentions_current: list
    :param mentions_previous: list of class mentions last known about
    :type mentions_previous: list
    """
    print(  # I have put the string on it's own line b/c PyCharm's formatter and PEP inspector want different things
            '{id}{_}{author}{_}{title}{_}{action}{_}{mentions_current}{_}{mentions_previous}'
                .format(
                    id = submission_.id,
                    author = submission_.author,
                    title = submission_.title,
                    action = action,
                    mentions_current = mentions_current,
                    mentions_previous = mentions_previous,
                    _ = '\t'))


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


def load_existing_posts_with_comments():
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
