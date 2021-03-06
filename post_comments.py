"""Loads mentions from the last run of find_mentions.py and posts comments to reddit.com."""

from typing import Optional, List, Dict
import praw
import db_core
import tools
from tools import trunc_pad
from tools import ExistingComment
import re

from db_core import CourseDatabase, Department, Course  # need this to de-pickle course_database.pickle
from mention_search_posts import PostWithMentions  # need this to de-pickle found_mentions.pickle

Existing_pwc = Dict[str, ExistingComment]  # type of existing_posts_with_comments


def _post_comment_helper(db, existing_posts_with_comments: Existing_pwc, new_mention_object: PostWithMentions,
                         reddit: praw.Reddit) -> bool:
    """Posts a comment on the submission with info about the courses mentioned.

    :param db: course database with info
    :type db: CourseDatabase
    :param new_mention_object: PostWithMentions object, which holds a post ID and a list of mentions
    :type new_mention_object: PostWithMentions
    :param reddit: authorized reddit praw object
    :type reddit: praw.Reddit
    :return: whether a comment was submitted or edited (based only on mentions, not on actually_do_it)
    :rtype: bool
    """
    submission_id = new_mention_object.post_id
    submission_obj = reddit.get_submission(submission_id = submission_id)

    mentions_new_unfiltered = new_mention_object.mentions_list

    # filter out mentions that don't match a class. (todo - find less shitty way to do this, probably try/except)
    mentions_new = [m for m in mentions_new_unfiltered if _mention_to_course_object(db, m) is not None]
    if not mentions_new:
        return False

    if submission_id in existing_posts_with_comments.keys():
        # if already have a comment with class info
        already_commented_obj = existing_posts_with_comments[submission_id]
        mentions_previous = already_commented_obj.mentions_list

        if mentions_new == mentions_previous:
            # if already have comment, but no new classes have been mentioned
            _print_csv_row(submission_obj, 'No new mentions.', mentions_new, mentions_previous)
            return False

        # comment needs to be updated
        existing_comment = reddit.get_info(thing_id = 't1_' + already_commented_obj.comment_id)
        existing_comment.edit(_get_comment(db, mentions_new))
        existing_posts_with_comments[submission_id].mentions_list = mentions_new
        tools.save_posts_with_comments(existing_posts_with_comments)
        _print_csv_row(submission_obj, 'Edited comment.', mentions_new, mentions_previous)
        return True

    else:
        # no comment with class info, post a new one
        new_comment = submission_obj.add_comment(_get_comment(db, mentions_new))
        existing_posts_with_comments[submission_id] = ExistingComment(new_comment.id, mentions_new)
        tools.save_posts_with_comments(existing_posts_with_comments)
        _print_csv_row(submission_obj, 'Comment added.', mentions_new, [])
        return True


def _get_comment(db: CourseDatabase, mention_list_: List[str]) -> Optional[str]:
    """Returns a markdown comment with info about the classes mentioned in the list.

    :param db: course database with info
    :type db: CourseDatabase
    :param mention_list_: list of mentions, like ['econ 1', 'cmps 5j']
    :type mention_list_: list
    :return: string of markdown comment
    :rtype str, None
    """
    if not mention_list_:  # if list is empty
        return None

    markdown_string = 'Classes mentioned in this thread:\n\n&nbsp;\n\n'

    for mention in mention_list_:
        course_obj = _mention_to_course_object(db, mention)
        if course_obj is None:
            continue
        markdown_string += _course_to_markdown(course_obj) + '&nbsp;\n\n'

    markdown_string += '---------------\n\n&nbsp;\n\n' + \
                       '*I am a bot. If I screw up, please comment or message me. ' + \
                       '[I\'m open source!](https://github.com/pfroud/ucsc-class-info-bot)*'

    return markdown_string


def _mention_to_course_object(db: CourseDatabase, mention_: str) -> Optional[Course]:
    """Converts mention of course to course object.

    :param db: course database with course info
    :type db: CourseDatabase
    :param mention_: string of course mention, like 'econ 1'
    :type mention_: str
    :return: course object from the mention
    :rtype: Course, None
    """
    split = mention_.split(' ')
    dept = split[0].lower()
    num = db_core.pad_course_num(split[1].upper())

    try:
        course_obj = db.depts[dept].courses[num]
    except KeyError:
        return None

    return course_obj


def _course_to_markdown(course: Course) -> str:
    """Returns a markdown representation of a course for use in reddit comments. Example:
    '**ECON 1: Into to Stuff**
    >We learn about econ and things.'

    :param course: Course to get markdown of
    :type course: Course
    :return: string of markdown of the course
    :rtype: str
    """

    num_leading_zeroes_stripped = re.sub("^0+", "", course.number)  # strip leading 0s only

    markdown_string = f'**{course.dept.upper()} {num_leading_zeroes_stripped}: {course.name}**\n'
    markdown_string += f'>{course.description}\n\n'

    return markdown_string


def _print_csv_row(submission, action: str, mentions_current: List[str], mentions_previous: List[str]) -> None:
    """Prints a CSV row to stdout to be used as a log about what happened with a comment.

    :param submission: Submission object that you are commenting on
    :type submission:  praw.objects.Submission
    :param action: string describing the action taken
    :type action: str
    :param mentions_current: list of current class mentions
    :type mentions_current: list
    :param mentions_previous: list of class mentions last known about
    :type mentions_previous: list
    """

    author = submission.author
    if author is None:
        author_name = "[deleted]"
    else:
        author_name = author.name

    print(" ".join([trunc_pad(submission.id, "id"),
                    trunc_pad(author_name, "author"),
                    trunc_pad(submission.title, "title"),
                    trunc_pad(action, "action"),
                    mentions_current,
                    mentions_previous]))


def post_comments(db: CourseDatabase, existing_posts_with_comments: Existing_pwc,
                  new_mentions_list: List[PostWithMentions], reddit: praw.Reddit) -> None:
    """Recursivley goes through the mentions found in the last run of mention_search_posts.py and
    posts a comment on each, if needed.

    :param existing_posts_with_comments: posts that we have already commented on
    :type existing_posts_with_comments: dict
    :param db: course database with info
    :type db: CourseDatabase
    :param new_mentions_list: list of mentions
    :type new_mentions_list: list
    :param reddit: authorized reddit praw object
    :type reddit: praw.Reddit
    """
    if new_mentions_list:
        new_mention = new_mentions_list.pop(0)
    else:
        print("No more mentions.")
        return
    _post_comment_helper(db, existing_posts_with_comments, new_mention, reddit)
    if __name__ == "__main__":
        tools.save_found_mentions(new_mentions_list)
    post_comments(db, existing_posts_with_comments, new_mentions_list, reddit)


def main():
    """something"""
    existing_posts_with_comments = tools.load_posts_with_comments()
    db = db_core.load_database()

    if __name__ == "__main__":
        print(" ".join([trunc_pad("id"),
                        trunc_pad("author"),
                        trunc_pad("title"),
                        trunc_pad("action")]))

        post_comments(db, existing_posts_with_comments, tools.load_found_mentions(), tools.auth_reddit())


main()
