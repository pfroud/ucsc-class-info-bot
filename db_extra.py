"""Stuff for the special cases for database build."""

import re
from db_core import Course, Department, DEBUG, regex_course_num, get_soup_object, has_course_number, get_course

lit_department_codes = {'Literature': 'lit',
                        'Creative Writing': 'ltcr',
                        'English-Language Literatures': 'ltel',
                        'French Literature': 'ltfr',
                        'German Literature': 'ltge',
                        'Greek Literature': 'ltgr',
                        'Latin Literature': 'ltin',
                        'Italian Literature': 'ltit',
                        'Modern Literary Studies': 'ltmo',
                        'Pre- and Early Modern Literature': 'ltpr',
                        'Spanish/Latin American/Latino Literatures': 'ltsp',
                        'World Literature and Cultural Studies': 'ltwl'}

# used only for college eight, those bastards
_regex_course_name = re.compile("[A-Za-z :']+\.?")


def is_last_course_in_p(strong_tag):
    """Whether the <strong> tag is in the last course in the paragraph.

    :param strong_tag: tag like <strong>1A.</strong>
    :type strong_tag: Tag
    :return: whether the tag is the last course in the paragraph
    :rtype: bool
    """
    strongs_in_parent_p = strong_tag.parent.find_all('strong')
    index = strongs_in_parent_p.index(strong_tag)
    distance_to_end = len(strongs_in_parent_p) - index
    return distance_to_end <= 4


def is_next_p_indented(num_tag):
    """Whether the next paragraph after this tag is indented.

    :param num_tag: tag like <strong>1A.</strong>
    :type num_tag: Tag
    :return: whether next paragraph is indented
    :rtype: bool
    """
    parent = num_tag.parent

    # special case for English-Language Literatures 102 (in lit page)
    if parent.name == 'strong':
        parent = parent.parent

    next_p = parent.next_sibling.next_sibling

    if next_p.name != 'p':
        return False

    return next_p.get('style') == 'margin-left: 30px;'


def in_indented_paragraph(num_tag):
    """Whether the tag is in an indented paragraph.

    :param num_tag: tag like <strong>1A.</strong>
    :type num_tag: Tag
    :return: whether tag is in indented paragraph
    :rtype: bool
    """
    return num_tag.parent.get('style') == 'margin-left: 30px;'


def get_course_all_in_one(dept_name, num_tag):
    """Makes a Course object when the whole heading is in one <strong> tag.
    DON'T NEED THIS ANY MORE EITHER!!!!!!!!

    :param dept_name: Name of the department the course is in
    :type dept_name: str
    :param num_tag: <strong> tag with the number, name, AND ges.
    :type num_tag: Tag
    :return: Course object
    :rtype: Course
    """
    strong_text = num_tag.text

    num_end = regex_course_num.match(strong_text).end()
    course_num = strong_text[0:num_end - 1]
    if DEBUG:
        print("doing", course_num)
    the_rest = strong_text[num_end + 1:]

    name_end = _regex_course_name.match(the_rest).end()
    course_name = the_rest[0:name_end - 1]

    if dept_name == 'havc':
        course_description = num_tag.next_sibling.next_sibling[1:]
    else:
        course_description = num_tag.next_sibling.next_sibling.next_sibling[1:]

    return Course(dept_name, course_num, course_name, course_description)


def get_first_course_no_bold(dept_name, first_strong_tag):
    """Gets the first course when the number is not bolded.
    Use only for germ and econ departments.
    DON'T NEED THIS ANY MORE!!!

    :param dept_name: name of the department like 'cmps'
    :type dept_name: str
    :param first_strong_tag: the first strong tag on the page, which is the name (not the number)
    :type: every_strong_tag: list
    :return: Course object of the first course listed
    :rtype: Course
    """
    number_1 = first_strong_tag.previous_sibling[1:-2]
    # print("\"" + number_1 + "\"")
    # print(first_tag.text[:-1])
    description = first_strong_tag.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling[2:]
    # print("\"" + description + "\"")
    return Course(dept_name, number_1, first_strong_tag.text[:-1], description)


def get_real_lit_dept(num_tag):
    """Gets the department for a course in the lit page, which has many sub-departments.

    :param num_tag: Tag of the number of a course
    :type: num_tag: Tag
    :return: name of the department the course actually is in
    :rtype str
    """
    parent = num_tag.parent

    while parent.name != 'h1':
        parent = parent.previous_sibling
    real_dept = parent.text

    return real_dept


def get_lit_depts():
    """Makes departments for all the sub-departments on the lit page.

    :return: list of Department objects
    :rtype: list
    """
    print("Building department \"lit\"...")

    lit_depts = dict()

    for dept_code in lit_department_codes.values():
        lit_depts[dept_code] = Department(dept_code)

    soup = get_soup_object('lit')
    every_strong_tag = soup.select("div.main-content strong")
    numbers_in_strongs = []
    for tag in every_strong_tag:
        if has_course_number(tag.text):
            numbers_in_strongs.append(tag)

    for num_tag in numbers_in_strongs:
        temp_course = get_course('lit', num_tag)
        if temp_course is None:
            continue
        lit_depts[temp_course.dept].add_course(temp_course)

    for dept in lit_depts.values():
        print('{_}{} courses added to \"{}\".'.format(str(len(dept.courses)), dept.name, _ = "...".rjust(28)))

    return list(lit_depts.values())
