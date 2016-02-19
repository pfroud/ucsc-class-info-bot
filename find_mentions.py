"""
Scrapes posts on /r/UCSC for mentions of courses.
"""

import re
import praw
import build_database  # used for pad_course_num() and load_database()
import tools
from tools import trunc_pad

_mention_regex = re.compile(" [0-9]+[A-Za-z]?")  # space is now required


class PostWithMentions:
    """Info about a specefic post and mentions found in that post."""

    def __init__(self, post_id, mentions_list):
        self.post_id = post_id
        self.mentions_list = mentions_list

    def __str__(self):
        return "mentions in post id {}: {}".format(self.post_id, self.mentions_list)


def _get_mentions_in_submission(submission_):
    """Finds mentions of a course in a submission's title, selftext, and comments.

    :param submission_: a praw submission object
    :type submission_: praw.objects.Submission
    :return: a PostWithMentions object which has the post ID and a list of strings of mentions
    :rtype: PostWithMentions
    """
    mentions_list = []
    mentions_list.extend(_get_mentions_in_string(submission_.title))

    mentions_list.extend(_get_mentions_in_string(submission_.selftext))

    flat_comments = praw.helpers.flatten_tree(submission_.comments)
    for comment in flat_comments:
        if comment.author is None or comment.author.name == 'ucsc-class-info-bot':
            continue
        mentions_list.extend(_get_mentions_in_string(comment.body))

    print('{id}{_}{author}{_}{title}{_}{mentions}'
          .format(id = trunc_pad(submission_.id, "id"),
                  author = trunc_pad(submission_.author.name, "author"),
                  title = trunc_pad(submission_.title, "title"),
                  mentions = mentions_list,
                  _ = '\t'))

    if not mentions_list:  # if list is empty
        return None
    else:
        return PostWithMentions(submission_.id, _remove_list_duplicates_preserve_order(mentions_list))


def _get_mentions_in_string(source_):
    """Finds mentions of courses (department and number) in a string.

    :param source_: string to look for courses in.
    :type source_: str
    :return: array of strings of course names
    :rtype: list
    """

    str_in = source_.lower()
    courses_found = []
    for subj in build_database.all_departments:  # iterate subjects

        # set start of search to beginning of string
        start_of_next_search = 0

        # search until reached end of string
        while start_of_next_search < len(str_in):

            # trim away part of string already searched through
            trimmed_str = str_in[start_of_next_search:]

            # run string search
            subj_start_index = trimmed_str.find(subj)

            if subj_start_index >= 0:  # if found a subject in body

                # set string index where subject ends
                subj_end_index = subj_start_index + len(subj)

                #  slice string to send to _mention_regex matcher. maximum of 5 extra chars needed
                regex_substr = trimmed_str[subj_end_index: subj_end_index + 5]

                # set next search to start after this one ends
                start_of_next_search += subj_end_index

                # search for course number
                regex_result = _mention_regex.match(regex_substr)
                if regex_result is not None:  # if found a class number

                    # string with subject and course number
                    subj_with_number = trimmed_str[subj_start_index: subj_end_index + regex_result.end()]

                    # move the start of next search past the number we found
                    start_of_next_search += regex_result.end()

                    courses_found.append(subj_with_number)

                    # print("matched string \"" + subj_with_number + "\".")
            else:
                break

    return courses_found


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
        if i not in new_list:
            new_list.append(i)

    return new_list


def find_mentions():
    """Finds and saves to disk course mentions in new posts on /r/UCSC."""

    reddit = tools.auth_reddit()

    # use this to find mentions in only one post
    # tools.save_found_mentions([_get_mentions_in_submission(reddit.get_submission(submission_id = "447b2j"))])
    # return

    print('{id}{_}{author}{_}{title}{_}mentions'
          .format(id = trunc_pad("id"),
                  author = trunc_pad("author"),
                  title = trunc_pad("title"),
                  _ = '\t'))

    subreddit = reddit.get_subreddit('ucsc')
    list_of_posts_with_mentions = []

    for submission in subreddit.get_new(limit = 3):
        found_mentions = _get_mentions_in_submission(submission)
        if found_mentions is not None:
            list_of_posts_with_mentions.append(found_mentions)

    tools.save_found_mentions(list_of_posts_with_mentions)

    print("------------------------------")
    for post_with_mention in list_of_posts_with_mentions:
        print(str(post_with_mention))


if __name__ == "__main__":
    find_mentions()
