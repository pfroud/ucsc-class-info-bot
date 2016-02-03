"""
Scrapes the self text and comments of a reddit submission for mentions of courses.
"""

import praw  # python wrapper for reddit api
import re  # regular expressions
import build_database  # used for pad_course_num() and load_database()
import tools
import pickle
import os.path


regex = re.compile(" ?[0-9]+[A-Za-z]?")


class PostWithMentions:
    """m"""

    def __init__(self, post_id, mentions_list):
        self.post_id = post_id
        self.mentions_list = mentions_list

    def __str__(self):
        return "mentions in post id {}: {}".format(self.post_id, self.mentions_list)


def get_mentions_in_submission(submission_):
    """Finds mentions of a course in a submission's title, selftext, and comments.

    :param submission_: a praw submission object
    :type submission_: praw.objects.Submission
    :return: an array of strings of course names
    :rtype: list
    """
    mentions_list = []
    mentions_list.extend(_get_mentions_in_string(submission_.title))

    mentions_list.extend(_get_mentions_in_string(submission_.selftext))

    flat_comments = praw.helpers.flatten_tree(submission_.comments)
    for comment in flat_comments:
        if comment.author.name == 'ucsc-class-info-bot':
            continue
        mentions_list.extend(_get_mentions_in_string(comment.body))

    print('{id}{_}{author}{_}{title}{_}{mentions}'
          .format(id = submission_.id,
                  author = submission_.author,
                  title = submission_.title,
                  mentions = mentions_list,
                  _ = '\t'))

    if not mentions_list:  # if list is empty
        return None
    else:
        return PostWithMentions(submission.id, _remove_list_duplicates_preserve_order(mentions_list))


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

                #  slice string to send to regex matcher. maximum of 5 extra chars needed
                regex_substr = trimmed_str[subj_end_index: subj_end_index + 5]

                # set next search to start after this one ends
                start_of_next_search += subj_end_index

                # search for course number
                regex_result = regex.match(regex_substr)
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

    :param input_list:
     :type input_list: list
    :return:
    :rtype: list
    """
    new_list = []

    for i in input_list:
        if i not in new_list:
            new_list.append(i)

    return new_list


def _save_found_mentions():
    with open("pickle/found_mentions.pickle", 'wb') as file:
        pickle.dump(list_of_posts_with_mentions, file)
    file.close()

# make sure saving found_mentions worked
# with open("pickle/found_mentions.pickle", 'rb') as file:
#     p_w_c = pickle.load(file)
# file.close()
# for post_with_mention in p_w_c:
#         print(str(post_with_mention))
# exit()

DEBUG = True
reddit = tools.auth_reddit()

if DEBUG:
    print('id{_}author{_}title{_}mentions'.format(_ = '\t'))

subreddit = reddit.get_subreddit('ucsc')
list_of_posts_with_mentions = []

for submission in subreddit.get_new(limit = 25):
    found_mentions = get_mentions_in_submission(submission)
    if found_mentions is not None:
        list_of_posts_with_mentions.append(found_mentions)

_save_found_mentions()

if DEBUG:
    print("------------------------------")
    for post_with_mention in list_of_posts_with_mentions:
        print(str(post_with_mention))
