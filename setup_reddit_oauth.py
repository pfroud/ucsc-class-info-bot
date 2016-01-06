"""Used to set up reddit api oauth. Also holds some methods for one-time use."""

import praw
import pickle


def get_code():
    """
    Use this first.
    Log into /u/ucsc-class-info-bot then navigate to the url printed.
    """
    url = reddit.get_authorize_url('state', 'identity submit edit read', True)
    print(url)


def save_access_information():
    """
    Use this second.
    Paste the code from the redirect into the function below.
    """
    with open('access_information.pickle', 'wb') as file:
        pickle.dump(reddit.get_access_information('code'), file)
    file.close()


reddit = praw.Reddit(user_agent = 'desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)',
                     site_name = 'ucsc_bot')

# get_code()
# save_access_information()


# print(posts_with_comments['3yw5sz'])
# exit()
# def rebuild_posts_with_comments():
#     """Make a new posts_with_comments file."""
#     submission = reddit.get_submission(submission_id='3yw5sz')  # the post on /r/bottesting
#     # posts_with_comments = dict()  # put this before call
#     the_comment = submission.comments[0]
#     posts_with_comments[submission.id] = ExistingComment(the_comment.id, get_mentions_in_submission(submission))
#     save_posts_with_comments()
# posts_with_comments = dict()
# rebuild_posts_with_comments()
# exit()
