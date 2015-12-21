"""
Given a string of a department and course number, pulls information about the course from the registrar.
"""

import requests
import re
from bs4 import BeautifulSoup

DEBUG = False

departments = ["acen", "aplx", "ams", "art", "artg", "astr", "bioc", "mcdb", "eeb", "bme", "chem", "chin", "clni",
               "clte", "cmmu", "cmpm", "cmpe", "cmps", "cowl", "cres", "crwn", "danm", "eart", "educ", "ee", "envs",
               "fmst", "film", "fren", "game", "gree", "hebr", "his", "hisc", "ital", "japn", "jwst", "krsg", "laad",
               "latn", "lals", "lgst", "ling", "math", "merr", "metx", "musc", "oaks", "ocea", "phil", "phye", "phys",
               "poli", "port", "punj", "russ", "scic", "socd", "socy", "span", "sphs", "stev", "tim", "thea", "ucdc",
               "writ", "yidd", 'prtr', 'anth', 'psyc']

lit_departments = {'Literature': 'lit',
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


# subsets of lit page: ltcr (creative writing), ltel (English-Language Literatures), ltfr (French Literature),
#    ltge (German Literature), ltgr (Greek Literature), ltin (latin literature), ltpr (Pre & Early Modern Literature),
#    ltmo (Modern Literary Studies), ltsp (Spanish/Latin Amer/Latino Lit), ltwl (World Lit & Cultural Studies), ltit
# taken out econ and germ because the 1 doesn't start bold


class CourseDatabase:
    """Holds a bunch of Departments, each of which hold a bunch of Courses."""

    def __init__(self):
        self.depts = dict()  # set up an empty dictionary

    def add_dept(self, new_dept):
        self.depts[new_dept.name] = new_dept

    def __str__(self):
        string = 'Database with ' + str(len(self.depts)) + ' department(s).\n'
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
        string = 'Department with ' + str(len(self.courses)) + " course(s).\n"
        for course_num, course_obj in sorted(self.courses.items()):
            string += '   ' + course_num + ': ' + str(course_obj) + '\n'
        return string


class Course:
    """Holds course name and description."""

    def __init__(self, dept, number, name, description):
        self.name = name
        self.description = description
        self.dept = dept
        self.number = number

    def __str__(self):
        return '\"' + self.name + "\""


# used in has_course_number() below
regex_course_num = re.compile("[0-9]+[A-Za-z]?\.")

# used only for college eight, those bastards
regex_course_name = re.compile("[A-Za-z :']+\.?")


def has_course_number(num_string):
    """Whether a string has a course number in it.

    :param num_string: string like '1.' or '1A.'
    :type num_string: str
    :return: whether the string contains a course number
    :rtype: bool
    """
    return regex_course_num.match(num_string) is not None


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
    return num_tag.parent.next_sibling.next_sibling.get('style') == 'margin-left: 30px;'


def in_indented_paragraph(num_tag):
    """Whether the tag is in an indented paragraph.

    :param num_tag: tag like <strong>1A.</strong>
    :type num_tag: Tag
    :return: whether tag is in indented paragraph
    :rtype: bool
    """
    return num_tag.parent.get('style') == 'margin-left: 30px;'


def get_soup_object(dept_name):
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


def course_from_num_tag(dept_name_orig, num_tag):
    """Builds and returns a Course object from the number specified.

    :param dept_name_orig: name of the department like 'cmps'
    :type dept_name_orig: str
    :param num_tag: tag of a course number, like <strong>21.</strong>
    :type num_tag: Tag
    :return: Course object of the specified course, or None if the course has sub-numbers
    :rtype: Course
    """
    number = num_tag.text[:-1]
    if DEBUG:
        print("doing", number)

    # extremely stupid special case
    if dept_name_orig == 'havc' and number == '152. Roman Eyes: Visual Culture and Power in the Ancient Roman World. ':
        if DEBUG:
            print('>>>>>>>>>> havc 152 special case')
        return course_from_num_tag_all_in_one('havc', num_tag)

    if is_last_course_in_p(num_tag) and is_next_p_indented(num_tag) and not in_indented_paragraph(num_tag):
        if DEBUG:
            print('   SKIPPING num_tag \"' + num_tag.text + "\"<<<<<<<<<<<<<<<<<<<<<")
        return None

    name_tag = num_tag.next_sibling.next_sibling
    name = name_tag.text[:-1]

    description_tag = name_tag.next_sibling.next_sibling

    while description_tag.name == 'strong' or description_tag.name == 'br' or description_tag.name == 'h2':
        description_tag = description_tag.next_sibling.next_sibling

    if description_tag.name == 'p':
        description_tag = description_tag.next_sibling

    description = description_tag[2:]
    return Course(dept_name_orig, number, name, description)


def course_from_num_tag_all_in_one(dept_name, num_tag):
    """

    :param num_tag:
    :return:
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


def build_department_object(dept_name_in):
    """Builds and returns a Department object with all courses.

    :param dept_name_in: name of the department to get classes for
    :type: dept_name_in: str
    :return: Department object of all the courses in the department
    :rtype: Department
    """
    if DEBUG:
        print("running on \"" + dept_name_in + "\"")

    new_dept = Department(dept_name_in)
    soup = get_soup_object(dept_name_in)

    every_strong_tag = soup.select("div.main-content strong")

    numbers_in_strongs = []

    for tag in every_strong_tag:
        if has_course_number(tag.text):
            numbers_in_strongs.append(tag)

    for num_tag in numbers_in_strongs:
        if dept_name_in == 'clei':
            new_dept.add_course(course_from_num_tag_all_in_one('clei', num_tag))
        else:
            new_dept.add_course(course_from_num_tag(dept_name_in, num_tag))

    return new_dept


# def add_lit_departments():
#     # http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/lit.html
#
#     soup = get_soup_object('lit')
#
#     current_h1 = soup.select("div.main-content h1")[0]
#
#     current_dept_name = current_h1.text
#     current_dept_code = lit_departments[current_dept_name]
#
#     pass


def build_database():
    """Builds and returns a CourseDatabase object

    :return: CourseDatabase object with all Departments
     :rtype: CourseDatabase
    """
    db = CourseDatabase()
    for current_dept in ['havc']:
        db.add_dept(build_department_object(current_dept))
    # add_lit_departments()
    return db


print(build_database())
