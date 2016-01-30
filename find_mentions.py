"""
Scrapes the self text and comments of a reddit submission for mentions of courses.
"""

from datetime import datetime
import praw  # python wrapper for reddit api
import re  # regular expressions
import database  # used for pad_course_num() and load_database()
# from database import CourseDatabase, Department, Course  # need this to de-pickle these classes

import reddit_tools

# http://praw.readthedocs.org/en/stable/pages/writing_a_bot.html
# http://praw.readthedocs.org/en/stable/pages/comment_parsing.html 


regex = re.compile(" ?[0-9]+[A-Za-z]?")


def _get_mentions_in_string(source_):
    """Finds mentions of courses (department and number) in a string.

    :param source_: string to look for courses in.
    :type source_: str
    :return: array of strings of course names
    :rtype: list
    """

    str_in = source_.lower()
    courses_found = []
    for subj in database.all_departments:  # iterate subjects

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


def get_mentions_in_submission(submission_):
    """Finds mentions of a course in a submission's title, selftext, and comments.

    :param submission_: a praw submission object
    :type submission_: praw.objects.Submission
    :return: an array of strings of course names
    :rtype: list
    """
    course_names = []
    course_names.extend(_get_mentions_in_string(submission_.title))

    course_names.extend(_get_mentions_in_string(submission_.selftext))

    flat_comments = praw.helpers.flatten_tree(submission_.comments)
    for comment in flat_comments:
        if comment.author.name == 'ucsc-class-info-bot':
            continue
        course_names.extend(_get_mentions_in_string(comment.body))

    return _remove_list_duplicates_preserve_order(course_names)


print('Started {}.'.format(datetime.now()))
posts_with_comments = reddit_tools.load_posts_with_comments()
db = database.load_database()
reddit = reddit_tools.auth_reddit()

print('id{_}author{_}title{_}action{_}current mentions{_}previous mentions'.format(_ = '\t'))

# post_comment(reddit.get_submission(submission_id = '3yw5sz'))  # on /r/bottesting
