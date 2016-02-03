"""
l
"""

import build_database
import find_mentions  # should remove after refactor done
import tools
import pickle


class ExistingComment:
    """Info about an existing comment with class info."""

    def __init__(self, comment_id_, mentions_):
        self.comment_id = comment_id_
        self.mentions_list = mentions_

    def __str__(self):
        return "\"{}\"->\"{}\"".format(self.comment_id, self.mentions_list)


def post_comment(submission_, actually_do_it = True):
    """Posts a comment on the submission with info about the courses mentioned

    :param submission_: submission object to post the comment to
    :type submission_: praw.objects.Submission
    :param actually_do_it: whether to actually post a comment to reddit.com
    :type actually_do_it: bool
    :return: message about the action taken.
    :rtype: str
    """
    submission_id = submission_.id

    mentions_current = find_mentions.get_mentions_in_submission(submission_)

    if not mentions_current:  # no mentions in the submission
        tools.print_csv_row(submission_, 'No mentions in thread.', [], [])
        return

    if submission_id in posts_with_comments.keys():  # already have a comment with class info
        already_commented_obj = posts_with_comments[submission_id]
        mentions_previous = already_commented_obj.mentions_list

        if mentions_current == mentions_previous:  # already commented, but no new classes have been mentioned
            tools.print_csv_row(submission_, 'No new mentions.', mentions_current, mentions_previous)
            return

        if actually_do_it:
            existing_comment = reddit.get_info(thing_id = 't1_' + already_commented_obj.comment_id)
            existing_comment.edit(_get_comment(db, mentions_current))
            posts_with_comments[submission_id].mentions_list = mentions_current
        tools.print_csv_row(submission_, 'Edited comment.', mentions_current, mentions_previous)

    else:  # no comment with class info, post a new one
        if actually_do_it:
            new_comment = submission_.add_comment(_get_comment(db, mentions_current))
            posts_with_comments[submission_id] = ExistingComment(new_comment.id, mentions_current)
        tools.print_csv_row(submission_, 'Comment added.', mentions_current, [])


def _course_to_markdown(course_):
    """Returns a markdown representation of a course for use in reddit comments. Example:
    '**ECON 1: Into to Stuff**
    >We learn about econ and things.'

    :param course_: Course to get markdown of
    :type course_: Course
    :return: string of markdown of the course
    :rtype: str
    """

    # TODO add the department name?
    # dept_name = dept_names[course_.dept]

    markdown_string = '**{} {}: {}**\n'.format(course_.dept.upper(), course_.number.strip('0'), course_.name)
    markdown_string += '>{}\n\n'.format(course_.description)

    return markdown_string


def _mention_to_course_object(db_, mention_):
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

    num = build_database.pad_course_num(split[1].upper())  # eventually get rid of this
    # num = split[1].upper()

    try:
        course_obj = db_.depts[dept].courses[num]
    except KeyError:
        return None

    return course_obj


def _get_comment(db_, mention_list_):
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
        course_obj = _mention_to_course_object(db_, mention)
        if course_obj is None:  # excepted Keyerror
            continue
        markdown_string += _course_to_markdown(course_obj) + '&nbsp;\n\n'

    markdown_string += '---------------\n\n&nbsp;\n\n' + \
                       '*I am a bot. If I screw up, please comment or message me. ' + \
                       '[I\'m open source!](https://github.com/pfroud/ucsc-class-info-bot)*'

    return markdown_string


def _load_found_mentions():
    with open("pickle/found_mentions.pickle", 'rb') as file:
        mentions = pickle.load(file)
    file.close()
    return mentions

db = build_database.load_database()
reddit = tools.auth_reddit()
posts_with_comments = tools.load_posts_with_comments()
found_mentions = _load_found_mentions()

# start here
