"""
Scrapes the self text and comments of a reddit submission for mentions of courses.
"""

import praw  # python wrapper for reddit api
import re  # regular expressions
import pickle  # serializer
import os.path
# from pprint import pprint
import database  # used for pad_course_num() and load_database()
from database import CourseDatabase, Department, Course  # need this to de-pickle these classes

# from get_course_info import get_course_object

# http://praw.readthedocs.org/en/stable/pages/writing_a_bot.html
# http://praw.readthedocs.org/en/stable/pages/comment_parsing.html 

# scraped from https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php

# previously " ?[0-9]+[A-Za-z]?"
regex = re.compile(" [0-9]+[A-Za-z]?")


def _get_mentions_in_string(db, source):
    """
    Finds mentions of courses (department and number) in a string.
    :param source: string to look for courses in.
    :return: array of strings of course names
    """

    str_in = source.lower()
    courses_found = []
    for subj in db.departments:  # iterate subjects

        # set start of search to beginning of string
        start_of_next_search = 0

        # search until reached end of sring
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

                    courses_found.append(subj_with_number)

                    # print("matched string \"" + subj_with_number + "\".")
            else:
                break

    return courses_found


def _get_mentions_in_submission(db, submission_in):
    """
    Finds mentions of a course in a submission's title, selftext, and comments.
    :param submission_in: a praw submission object
    :return: an array of strings of course names
    """
    course_names = []
    course_names.extend(_get_mentions_in_string(db, submission_in.title))

    course_names.extend(_get_mentions_in_string(db, submission_in.selftext))

    flat_comments = praw.helpers.flatten_tree(submission_in.comments)
    for comment in flat_comments:
        course_names.extend(_get_mentions_in_string(db, comment.body))

    # the list(set()) thing removes duplicates
    return list(set(course_names))


def auth_reddit():
    """

    :return:
    """
    red = praw.Reddit(user_agent='desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)', site_name='ucsc_bot')
    with open('access_information.pickle', 'rb') as file:
        access_information = pickle.load(file)
    file.close()
    red.set_access_credentials(**access_information)
    return red


def _get_course_obj_from_mention(db, mention):
    split = mention.split(' ')
    dept = split[0]
    num = database.pad_course_num(split[1].upper())
    # num = split[1].upper()
    course_obj = db.depts[dept].courses[num]
    return course_obj


def _get_markdown(db, mention_list):
    if not mention_list:  # if list is empty
        return None

    markdown_string = ''

    for mention in mention_list:
        course_obj = _get_course_obj_from_mention(db, mention)
        markdown_string += _course_to_markdown(course_obj)
        markdown_string += '&nbsp;\n\n'

    markdown_string += '---------------\n\n&nbsp;\n\n'
    markdown_string += '*I am a bot. If I screw up, please comment or message me. ' + \
                       '[I\'m open source!](https://github.com/pfroud/ucsc-class-info-bot)*'

    return markdown_string


submission_pickle_path = os.path.join(os.path.dirname(__file__), 'submission.pickle')


def _course_to_markdown(course):
    """Returns a markdown representation of a course for use in reddit comments. Example:
    '**ECON 1: Into to Stuff**
    >We learn about econ and things.'

    :param course: Course to get markdown of
    :type course: Course
    :return: string of markdown of the course
    :rtype: str
    """
    markdown_string = '**{} {}: {}**\n'.format(course.dept.upper(), course.number.strip('0'), course.name)
    markdown_string += '>{}\n\n'.format(course.description)

    return markdown_string


def _save_submission(sub):
    with open(submission_pickle_path, 'wb') as file:
        pickle.dump(sub, file)
    file.close()


def _load_submission():
    with open(submission_pickle_path, 'rb') as file:
        sub = pickle.load(file)
    file.close()
    return sub


# url = r.get_authorize_url('state', 'identity submit edit', True)
# print(url)

# with open(r'C:\Users\Peter Froud\Documents\reddit ucsc bot\access_information.pickle', 'wb') as file:
#     pickle.dump(r.get_access_information('code'), file)
# file.close()

# r = auth_reddit()

the_db = database.load_database()

thing = _get_markdown(the_db, ['cmps 5j', 'ams 131', 'lit 1', 'chem 109'])

print(thing)

# print('>getting PRAW')
# r = praw.Reddit(user_agent='desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)')

# print('>getting submission')
# submission = r.get_submission(submission_id='3w0wt4')
# submission = _load_submission()

# print('>finding mentions')
# mentions = _get_mentions_in_submission(submission)
# print(mentions)
# for m in mentions:
#     print(_get_course_obj_from_mention(m))

# subreddit = r.get_subreddit('ucsc')
# for submission in subreddit.get_new():
#     print(submission)
#     print(_get_mentions_in_submission(submission))
#     print('-------------------')
