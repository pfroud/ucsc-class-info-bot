"""
Scrapes the self text and comments of a reddit submission for mentions of courses.
"""

import praw  # python wrapper for reddit api
import re  # regular expressions
import pickle
from pprint import pprint
from database import load_database, pad_course_num, CourseDatabase, Department, Course

# from get_course_info import get_course_object

# http://praw.readthedocs.org/en/stable/pages/writing_a_bot.html
# http://praw.readthedocs.org/en/stable/pages/comment_parsing.html 

# scraped from https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php
subjects = ["ACEN", "AMST", "ANTH", "APLX", "AMS", "ARAB", "ART", "ARTG", "ASTR", "BIOC", "BIOL", "BIOE", "BME", "CHEM",
            "CHIN", "CLEI", "CLNI", "CLTE", "CMMU", "CMPM", "CMPE", "CMPS", "COWL", "LTCR", "CRES", "CRWN", "DANM",
            "EART", "ECON", "EDUC", "EE", "ENGR", "LTEL", "ENVS", "ETOX", "FMST", "FILM", "FREN", "LTFR", "GAME",
            "GERM", "LTGE", "GREE", "LTGR", "HEBR", "HNDI", "HIS", "HAVC", "HISC", "HUMN", "ISM", "ITAL", "LTIT",
            "JAPN", "JWST", "KRSG", "LAAD", "LATN", "LALS", "LTIN", "LGST", "LING", "LIT", "MATH", "MERR", "METX",
            "LTMO", "MUSC", "OAKS", "OCEA", "PHIL", "PHYE", "PHYS", "POLI", "PRTR", "PORT", "LTPR", "PSYC", "PUNJ",
            "RUSS", "SCIC", "SOCD", "SOCS", "SOCY", "SPAN", "SPHS", "SPSS", "LTSP", "STEV", "TIM", "THEA", "UCDC",
            "WMST", "LTWL", "WRIT", "YIDD", "CE", "CS"]
subjects_lower = [x.lower() for x in subjects]

# previously " ?[0-9]+[A-Za-z]?"
regex = re.compile(" [0-9]+[A-Za-z]?")


def get_mentions_in_string(source):
    """
    Finds mentions of courses (department and number) in a string.
    :param source: string to look for courses in.
    :return: array of strings of course names
    """

    str_in = source.lower()
    courses_found = []
    for subj in subjects_lower:  # iterate subjects

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


def get_mentions_in_submission(submission_in):
    """
    Finds mentions of a course in a submission's title, selftext, and comments.
    :param submission_in: a praw submission object
    :return: an array of strings of course names
    """
    course_names = []
    course_names.extend(get_mentions_in_string(submission_in.title))

    course_names.extend(get_mentions_in_string(submission_in.selftext))

    flat_comments = praw.helpers.flatten_tree(submission_in.comments)
    for comment in flat_comments:
        course_names.extend(get_mentions_in_string(comment.body))

    # the list(set()) thing removes duplicates
    return list(set(course_names))


def auth_reddit():
    """

    :return:
    """
    red = praw.Reddit(user_agent='desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)', site_name='ucsc_bot')
    with open('access_information_pickle', 'rb') as file:
        access_information = pickle.load(file)
    file.close()
    red.set_access_credentials(**access_information)
    return red


def get_course_obj_from_mention(mention):
    split = mention.split(' ')
    dept = split[0]
    num = pad_course_num(split[1].upper())
    course_obj = db.depts[dept].courses[num]
    return course_obj


def save_submission(sub):
    with open(r'C:\Users\Peter Froud\Documents\reddit ucsc bot\submission_pickle', 'wb') as file:
        pickle.dump(sub, file)
    file.close()


def load_submission():
    with open(r'C:\Users\Peter Froud\Documents\reddit ucsc bot\submission_pickle', 'rb') as file:
        sub = pickle.load(file)
    file.close()
    return sub

# url = r.get_authorize_url('bananaphone', 'identity submit edit', True)
# print(url)

# with open(r'C:\Users\Peter Froud\Documents\reddit ucsc bot\access_information_pickle', 'wb') as file:
#     pickle.dump(r.get_access_information('code'), file)
# file.close()

# r = auth_reddit()

# print('>loading database')
db = load_database()

# print('>getting PRAW')
# r = praw.Reddit(user_agent='desktop:ucsc-class-info-bot:v0.0.1 (by /u/ucsc-class-info-bot)')

# print('>getting submission')
# submission = r.get_submission(submission_id='3w0wt4')
submission = load_submission()

# print('>finding mentions')
mentions = get_mentions_in_submission(submission)

for m in mentions:
    print(get_course_obj_from_mention(m))
