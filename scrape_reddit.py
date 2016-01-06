"""
Scrapes the self text and comments of a reddit submission for mentions of courses.
"""
from datetime import datetime
import praw  # python wrapper for reddit api
import re  # regular expressions
import pickle  # serializer
import os.path
from pprint import pprint
from dept_names import dept_names
import database  # used for pad_course_num() and load_database()
from database import CourseDatabase, Department, Course  # need this to de-pickle these classes

# http://praw.readthedocs.org/en/stable/pages/writing_a_bot.html
# http://praw.readthedocs.org/en/stable/pages/comment_parsing.html 


# previously " ?[0-9]+[A-Za-z]?"
regex = re.compile(" [0-9]+[A-Za-z]?")


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


def _get_course_obj_from_mention(db_, mention_):
    """Converts mention of course to course object

    :param db_: course database with course info
    :type db_: CourseDatabase
    :param mention_: string of course mention, like 'econ 1'
    :type mention_: str
    :return: course database from the mention
    :rtype: Course
    """
    split = mention_.split(' ')

    dept = split[0].lower()
    # if dept == 'cs':
    #     dept = 'cmps'
    # if dept == 'ce':
    #     dept = 'cmpe'

    num = database.pad_course_num(split[1].upper())
    # num = split[1].upper()

    try:
        course_obj = db_.depts[dept].courses[num]
    except KeyError:
        return None

    return course_obj


def get_markdown(db_, mention_list_):
    """Returns a markdown comment with info about the classes mentioned in the list

    :param db_: course database with info
    :type db_: CourseDatabase
    :param mention_list_: list of mentions, like ['econ 1', 'cmps 5j']
    :type mention_list_: list
    :return: string of markdown comment
    :rtype str
    """
    if not mention_list_:  # if list is empty
        return None

    markdown_string = 'Classes mentioned in this thread:\n\n&nbsp;\n\n'

    for mention in mention_list_:
        course_obj = _get_course_obj_from_mention(db_, mention)
        if course_obj is None:  # excepted Keyerror
            continue
        markdown_string += _course_to_markdown(course_obj) + '&nbsp;\n\n'

    markdown_string += '---------------\n\n&nbsp;\n\n' + \
                       '*I am a bot. If I screw up, please comment or message me. ' + \
                       '[I\'m open source!](https://github.com/pfroud/ucsc-class-info-bot)*'

    return markdown_string


posts_with_comments_pickle_path = os.path.join(os.path.dirname(__file__), 'posts_with_comments.pickle')


def _course_to_markdown(course_):
    """Returns a markdown representation of a course for use in reddit comments. Example:
    '**ECON 1: Into to Stuff**
    >We learn about econ and things.'

    :param course_: Course to get markdown of
    :type course_: Course
    :return: string of markdown of the course
    :rtype: str
    """

    # TODO
    # add the department name?
    # dept_name = dept_names[course_.dept]

    markdown_string = '**{} {}: {}**\n'.format(course_.dept.upper(), course_.number.strip('0'), course_.name)
    markdown_string += '>{}\n\n'.format(course_.description)

    return markdown_string


def save_posts_with_comments():
    """Saves to disk the dict of posts that have already been commented on"""
    with open(posts_with_comments_pickle_path, 'wb') as file:
        pickle.dump(posts_with_comments, file)
    file.close()


def load_posts_with_comments():
    """Loads from disk the dict of posts that have already been commented on

    :return: dict of posts that have already been commented on
    :rtype: dict
    """
    with open(posts_with_comments_pickle_path, 'rb') as file:
        a_c = pickle.load(file)
    file.close()
    return a_c


def post_comment(submission_):
    """Posts a comment on the submission with info about the courses mentioned

    :param submission_: submission object to post the comment to
    :type submission_: praw.objects.Submission
    :return: message about the action taken.
    :rtype: str
    """
    submission_id = submission_.id

    mentions_current = get_mentions_in_submission(submission_)

    if not mentions_current:  # no mentions in the submission
        print_csv_row(submission_, 'No mentions in thread.', [], [])
        return

    if submission_id in posts_with_comments.keys():  # already have a comment with class info
        already_commented_obj = posts_with_comments[submission_id]
        mentions_previous = already_commented_obj.mentions_list

        if mentions_current == mentions_previous:  # already commented, but no new classes have been mentioned
            print_csv_row(submission_, 'No new mentions.', mentions_current, mentions_previous)
            return

        existing_comment = reddit.get_info(thing_id = 't1_' + already_commented_obj.comment_id)
        existing_comment.edit(get_markdown(db, mentions_current))
        posts_with_comments[submission_id].mentions_list = mentions_current
        print_csv_row(submission_, 'Edited comment.', mentions_current, mentions_previous)
    else:
        new_comment = submission_.add_comment(get_markdown(db, mentions_current))
        posts_with_comments[submission_id] = ExistingComment(new_comment.id, mentions_current)
        print_csv_row(submission_, 'Comment added.', mentions_current, [])


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


class ExistingComment:
    """Info about an existing comment with class info."""

    def __init__(self, comment_id_, mentions_):
        self.comment_id = comment_id_
        self.mentions_list = mentions_

    def __str__(self):
        return "\"{}\"->\"{}\"".format(self.comment_id, self.mentions_list)


# print('Started {}.'.format(datetime.now()))
posts_with_comments = load_posts_with_comments()
db = database.load_database()
reddit = auth_reddit()

print('id{_}author{_}title{_}action{_}current mentions{_}previous mentions'.format(_ = '\t'))

post_comment(reddit.get_submission(submission_id = '3yw5sz'))  # on /r/bottesting

# subreddit = reddit.get_subreddit('ucsc')
# for submission in subreddit.get_new():
#     # print(submission)
#     post_comment(submission)

save_posts_with_comments()
