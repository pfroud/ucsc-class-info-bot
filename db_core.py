"""
Given a string of a department and course number, pulls information about the course from the registrar.
"""

from typing import Optional
import requests  # pulls registrar pages
import re  # regular expressions
from bs4 import BeautifulSoup  # html parser
import pickle  # serializer
import os.path  # check if file exists, get file size
from datetime import datetime  # added to output logs
import sys  # print without newline

DEBUG = False

_all_departments = [
    "acen", "aplx", "ams", "art", "artg", "astr", "bioc", "mcdb", "eeb", "bme", "chem", "chin", "clni", "clte", "cmmu",
    "cmpm", "cmpe", "cmps", "cowl", "cres", "crwn", "danm", "eart", "educ", "ee", "envs", "fmst", "film", "fren",
    "game", "gree", "hebr", "his", "hisc", "ital", "japn", "jwst", "krsg", "laad", "latn", "lals", "lgst", "ling",
    "math", "merr", "metx", "musc", "oaks", "ocea", "phil", "phye", "phys", "poli", "port", "punj", "russ", "scic",
    "socd", "socy", "span", "sphs", "stev", "tim", "thea", "ucdc", "writ", "yidd", 'prtr', 'anth', 'psyc', 'havc',
    'clei', 'econ', 'germ']

# used in has_course_number() below
regex_course_num = re.compile("[0-9]+[A-Za-z]?\.")


class CourseDatabase:
    """Holds a bunch of Departments, each of which hold a bunch of Courses."""

    def __init__(self):
        self.depts = {}
        self.num_courses = 0

    def add_dept(self, new_dept: Department) -> None:
        """Add a department to the course database.
        :param new_dept: Department object to add
        :type new_dept: Department
        """
        self.depts[new_dept.name] = new_dept
        self.num_courses += len(new_dept.courses)

    def __str__(self) -> str:
        string = f'Database with {self.num_courses} course(s) in {len(self.depts)} department(s).\n'
        for dept_num, dept_obj in sorted(self.depts.items()):
            string += '\n' + dept_num + ': ' + str(dept_obj)
        return string


class Department:
    """Holds a bunch of Courses."""

    def __init__(self, name):
        self.courses = {}
        self.name = name

    def add_course(self, new_course: Course) -> None:
        """Adds a course to the department.
        :param new_course: Course to add.
        :type new_course: Course
        """
        if new_course is not None:
            self.courses[new_course.number] = new_course

    def __str__(self) -> str:
        string = f'Department with {len(self.courses)} course(s).\n'
        for course_num, course_obj in sorted(self.courses.items()):
            string += '   ' + course_num.ljust(4) + ': ' + str(course_obj) + '\n'
        return string


def pad_course_num(number: str) -> str:
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

    def __init__(self, dept_name: str, number: str, name: str, description: str):
        self.dept = dept_name
        self.number = pad_course_num(number)
        self.name = name
        self.description = description

    def __str__(self) -> str:
        # return "{} {}: {}".format(self.dept, self.number, self.name)
        return f'"{self.name}"'


def has_course_number(num_string: str) -> bool:
    """Whether a string has a course number in it.

    :param num_string: string like '1.' or '1A.'
    :type num_string: str
    :return: whether the string contains a course number
    :rtype: bool
    """
    return regex_course_num.match(num_string) is not None


def get_soup_object(dept_name: str) -> BeautifulSoup:
    """Requests a page from the registrar and returns a BeautifulSoup object of it.

    :param dept_name: string like 'cmps'
    :type dept_name: str
    :return: BeautifulSoup object of the department's courses
    :rtype: BeautifulSoup
    """
    url = "http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/" + dept_name + ".html"

    request_result = requests.get(url)
    request_result.raise_for_status()
    return BeautifulSoup(request_result.text, 'html.parser')


def get_course(dept_name: str, num_tag) -> Optional[Course]:
    """Builds and returns a Course object from the number specified.
    If the <strong> tag has more than just the number in it, use get_course_all_in_one().

    :param dept_name: name of the department like 'cmps'
    :type dept_name: str
    :param num_tag: tag of a course number, like <strong>21.</strong>
    :type num_tag: Tag
    :return: Course object of the specified course, or None if the course has sub-numbers
    :rtype: Course, None
    """
    course_num = num_tag.text[:-1]
    if DEBUG:
        print("doing", course_num)

    # extremely stupid special case
    if dept_name == 'havc' and course_num == '152. Roman Eyes: Visual Culture and Power in the Ancient Roman World. ':
        if DEBUG:
            print('>>>>>>>>>> havc 152 special case')
        return extras.get_course_all_in_one('havc', num_tag)

    if extras.is_last_course_in_p(num_tag) and extras.is_next_p_indented(num_tag) and not \
            extras.in_indented_paragraph(num_tag):
        if DEBUG:
            print(f'   SKIPPING num_tag "{num_tag.text}"')
        return None

    # TODO change .next_sibling.next_sibling to next_siblings[1]
    name_tag = num_tag.next_sibling.next_sibling
    course_name = name_tag.text.strip(' .')

    descr_tag = name_tag.next_sibling.next_sibling

    while descr_tag.name == 'strong' or descr_tag.name == 'br' or descr_tag.name == 'h2':
        descr_tag = descr_tag.next_sibling.next_sibling

    if descr_tag.name == 'p':
        descr_tag = descr_tag.next_sibling

    descr_str = descr_tag[2:]

    if dept_name == 'lit':
        real_dept_name = extras.get_real_lit_dept(num_tag).replace("\ufeff", "")  # remove byte order mark
        if DEBUG:
            print(f'   real name is "{real_dept_name}"')

        # Russian Lit department has no dept code, probably does not actually exist
        if real_dept_name == 'Russian Literature':
            return None

        return Course(extras.lit_department_codes[real_dept_name], course_num, course_name, descr_str)
    else:
        return Course(dept_name, course_num, course_name, descr_str)


def _get_department_object(dept_name: str) -> Department:
    """Builds and returns a Department object with all courses.

    :param dept_name: name of the department to get classes for
    :type dept_name: str
    :return: Department object of all the courses in the department
    :rtype: Department
    """
    # if DEBUG:
    sys.stdout.write(f'Building department "{dept_name}"')

    soup = get_soup_object(dept_name)

    # registrar url has EEB, courses use dept code BIOE
    if dept_name == 'eeb':
        dept_name = 'bioe'
        sys.stdout.write(f"changed name to {dept_name}...")

    # registrar url has MCDB, courses use dept code BIOL
    if dept_name == 'mcdb':
        dept_name = 'biol'
        sys.stdout.write(f"changed name to {dept_name}...")

    new_dept = Department(dept_name)

    every_strong_tag = soup.select("div.main-content strong")
    strong_tags_with_course_nums = []

    for tag in every_strong_tag:
        if has_course_number(tag.text):
            strong_tags_with_course_nums.append(tag)

    for num_tag in strong_tags_with_course_nums:
        if dept_name == 'clei':
            new_dept.add_course(extras.get_course_all_in_one('clei', num_tag))
        else:
            new_dept.add_course(get_course(dept_name, num_tag))

    if dept_name == 'germ' or dept_name == 'econ':
        new_dept.add_course(extras.get_first_course_no_bold(dept_name, every_strong_tag[0]))

    sys.stdout.write(str(len(new_dept.courses)) + ' courses added.\n')

    return new_dept


def _build_database() -> CourseDatabase:
    """Builds and returns a CourseDatabase object.

    :return: CourseDatabase object with all Departments
    :rtype: CourseDatabase
    """
    print(f'Starting the database build on {datetime.now()}.')
    print('----------------------------------')
    db = CourseDatabase()

    for current_dept in _all_departments:
        db.add_dept(_get_department_object(current_dept))

    for lit_dept in extras.get_lit_depts():
        db.add_dept(lit_dept)
    return db


_database_pickle_path = os.path.join(os.path.dirname(__file__), r'pickle\course_database.pickle')


def _save_database() -> None:
    """Builds and saves a new database to a file on disk."""
    if os.path.isfile(_database_pickle_path):
        print('save_database(): database already exists. Use load_database() instead.')
        return

    db = _build_database()

    with open(_database_pickle_path, 'wb') as file:
        pickle.dump(db, file)
    file.close()
    print('----------------------------------')
    print(f'Wrote {os.path.getsize(_database_pickle_path):,} bytes to path "{_database_pickle_path}".\n')


def load_database() -> CourseDatabase:
    """Reads a course database from file on disk.

    :return: course database read from file
    :rtype: CourseDatabase
    """
    with open(_database_pickle_path, 'rb') as file:
        db = pickle.load(file)
    file.close()
    return db


if __name__ == "__main__":
    import db_extra as extras

    _save_database()
    # print(load_database())
