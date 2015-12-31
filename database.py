"""
Given a string of a department and course number, pulls information about the course from the registrar.
"""

import requests  # pulls registrar pages
import re  # regular expressions
from bs4 import BeautifulSoup  # html parser
import pickle  # serializer
import os.path  # check if file exists, get file size
import datetime  # added to output logs
import sys  # print without newline

DEBUG = False

departments = ["acen", "aplx", "ams", "art", "artg", "astr", "bioc", "mcdb", "eeb", "bme", "chem", "chin", "clni",
               "clte", "cmmu", "cmpm", "cmpe", "cmps", "cowl", "cres", "crwn", "danm", "eart", "educ", "ee", "envs",
               "fmst", "film", "fren", "game", "gree", "hebr", "his", "hisc", "ital", "japn", "jwst", "krsg", "laad",
               "latn", "lals", "lgst", "ling", "math", "merr", "metx", "musc", "oaks", "ocea", "phil", "phye", "phys",
               "poli", "port", "punj", "russ", "scic", "socd", "socy", "span", "sphs", "stev", "tim", "thea", "ucdc",
               "writ", "yidd", 'prtr', 'anth', 'psyc', 'havc', 'clei', 'econ', 'germ', 'lit']

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

# used in _has_course_number() below
regex_course_num = re.compile("[0-9]+[A-Za-z]?\.")

# used only for college eight, those bastards
regex_course_name = re.compile("[A-Za-z :']+\.?")


class CourseDatabase:
    """Holds a bunch of Departments, each of which hold a bunch of Courses."""

    def __init__(self):
        self.depts = dict()  # set up an empty dictionary
        self.num_courses = 0

    def add_dept(self, new_dept):
        self.depts[new_dept.name] = new_dept
        self.num_courses += len(new_dept.courses)

    def __str__(self):
        string = 'Database with {} course(s) in {} department(s).\n'.format(self.num_courses, len(self.depts))
        for dept_num, dept_obj in sorted(self.depts.items()):
            string += '\n' + dept_num + ': ' + str(dept_obj)
        return string


class Department:
    """Holds a bunch of Courses."""

    def __init__(self, name):
        self.courses = dict()
        self.name = name

    def add_course(self, new_course):
        if new_course is not None:
            self.courses[new_course.number] = new_course

    def __str__(self):
        string = 'Department with {} course(s).\n'.format(len(self.courses))
        for course_num, course_obj in sorted(self.courses.items()):
            string += '   ' + course_num.ljust(4) + ': ' + str(course_obj) + '\n'
        return string


def pad_course_num(number):
    """Adds leading zeroes to course numbers.
    '3' -> '003'; '3A' -> '003A'; '100' and '100A' unchanged.

    :param number: course number to pad
    :type number: str
    :return: padded course number
    :rtype: str
    """
    if number[-1].isalpha():
        return number.zfill(4)
    else:
        return number.zfill(3)


class Course:
    """Holds course name and description."""

    def __init__(self, dept, number, name, description):
        self.dept = dept
        self.number = pad_course_num(number)
        # self.number = number
        self.name = name
        self.description = description

    def __str__(self):
        # return self.dept + ' ' + self.number + ': ' + self.name
        return '\"' + self.name + "\""


def _has_course_number(num_string):
    """Whether a string has a course number in it.

    :param num_string: string like '1.' or '1A.'
    :type num_string: str
    :return: whether the string contains a course number
    :rtype: bool
    """
    return regex_course_num.match(num_string) is not None


def _is_last_course_in_p(strong_tag):
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


def _is_next_p_indented(num_tag):
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


def _in_indented_paragraph(num_tag):
    """Whether the tag is in an indented paragraph.

    :param num_tag: tag like <strong>1A.</strong>
    :type num_tag: Tag
    :return: whether tag is in indented paragraph
    :rtype: bool
    """
    return num_tag.parent.get('style') == 'margin-left: 30px;'


def _get_soup_object(dept_name):
    """Requests a page from the registrar and returns a BeautifulSoup object of it.

    :param dept_name: string like 'cmps'
    :type dept_name: str
    :return: BeautifulSoup object of the department's courses
    :rtype: BeautifulSoup
    """
    url = "http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/" + dept_name + ".html"

    request_result = requests.get(url)

    status_code = request_result.status_code
    if status_code != 200:
        raise Exception(url + ' returned ' + str(status_code) + '\n')

    return BeautifulSoup(request_result.text, 'html.parser')


def _get_course(dept_name, num_tag):
    """Builds and returns a Course object from the number specified.
    If the <strong> tag has more than just the number in it, use _get_course_all_in_one().

    :param dept_name: name of the department like 'cmps'
    :type dept_name: str
    :param num_tag: tag of a course number, like <strong>21.</strong>
    :type num_tag: Tag
    :return: Course object of the specified course, or None if the course has sub-numbers
    :rtype: Course
    """
    number = num_tag.text[:-1]
    if DEBUG:
        print("doing", number)

    # extremely stupid special case
    if dept_name == 'havc' and number == '152. Roman Eyes: Visual Culture and Power in the Ancient Roman World. ':
        if DEBUG:
            print('>>>>>>>>>> havc 152 special case')
        return _get_course_all_in_one('havc', num_tag)

    if _is_last_course_in_p(num_tag) and _is_next_p_indented(num_tag) and not _in_indented_paragraph(num_tag):
        if DEBUG:
            print('   SKIPPING num_tag \"' + num_tag.text + "\"<<<<<<<<<<<<<<<<<<<<<")
        return None

    name_tag = num_tag.next_sibling.next_sibling
    name = name_tag.text.strip(' .')

    description_tag = name_tag.next_sibling.next_sibling

    while description_tag.name == 'strong' or description_tag.name == 'br' or description_tag.name == 'h2':
        description_tag = description_tag.next_sibling.next_sibling

    if description_tag.name == 'p':
        description_tag = description_tag.next_sibling

    description = description_tag[2:]

    if dept_name in lit_department_codes.values():
        real_name = _get_real_lit_dept(num_tag).replace("\ufeff", "")
        # print("   real name is \"" + real_name + "\"")

        # Russian Lit department has no dept code, probably does not actually exist
        if real_name == 'Russian Literature':
            return None

        return Course(lit_department_codes[real_name], number, name, description)
    else:
        return Course(dept_name, number, name, description)


def _get_course_all_in_one(dept_name, num_tag):
    """Makes a Course object when the whole heading is in one <strong> tag.

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

    name_end = regex_course_name.match(the_rest).end()
    course_name = the_rest[0:name_end - 1]

    if dept_name == 'havc':
        course_description = num_tag.next_sibling.next_sibling[1:]
    else:
        course_description = num_tag.next_sibling.next_sibling.next_sibling[1:]

    return Course(dept_name, course_num, course_name, course_description)


def _get_first_course_no_bold(dept_name, first_strong_tag):
    """Gets the first course when the number is not bolded.
    Use only for germ and econ departments.

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


def _get_department_object(dept_name):
    """Builds and returns a Department object with all courses.

    :param dept_name: name of the department to get classes for
    :type dept_name: str
    :return: Department object of all the courses in the department
    :rtype: Department
    """
    # if DEBUG:
    sys.stdout.write("Building department \"" + dept_name + "\"...")

    new_dept = Department(dept_name)
    soup = _get_soup_object(dept_name)

    every_strong_tag = soup.select("div.main-content strong")

    numbers_in_strongs = []

    for tag in every_strong_tag:
        if _has_course_number(tag.text):
            numbers_in_strongs.append(tag)

    for num_tag in numbers_in_strongs:
        if dept_name == 'clei':
            new_dept.add_course(_get_course_all_in_one('clei', num_tag))
        else:
            new_dept.add_course(_get_course(dept_name, num_tag))

    if dept_name == 'germ' or dept_name == 'econ':
        new_dept.add_course((_get_first_course_no_bold(dept_name, every_strong_tag[0])))

    sys.stdout.write(str(len(new_dept.courses)) + ' courses added.\n')

    return new_dept


def _get_real_lit_dept(num_tag):
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


def build_database():
    """Builds and returns a CourseDatabase object.

    :return: CourseDatabase object with all Departments
    :rtype: CourseDatabase
    """
    print('Starting the database build on {}.'.format(datetime.datetime.now()))
    print('----------------------------------')
    db = CourseDatabase()
    for current_dept in departments:
        db.add_dept(_get_department_object(current_dept))
    return db


database_pickle_path = os.path.join(os.path.dirname(__file__), r'database_files\course_database.pickle')


def save_database():
    """

    :return:
    """
    if os.path.isfile(database_pickle_path):
        print('save_database(): database already exists. Use load_database() instead.')
        return

    db = build_database()

    with open(database_pickle_path, 'wb') as file:
        pickle.dump(db, file)
    file.close()
    print('----------------------------------')
    print('Wrote {:,} bytes to path \"{}\".\n'.format(os.path.getsize(database_pickle_path), database_pickle_path))
    return db


def load_database():
    """

    :return:
    """
    with open(database_pickle_path, 'rb') as file:
        db = pickle.load(file)
    file.close()
    return db
